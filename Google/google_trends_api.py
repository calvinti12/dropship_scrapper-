# https://pypi.org/project/pytrends/#interest-by-region
from random import shuffle

from aiohttp import ClientSession
from pytrends.request import TrendReq
import pandas as pd
from adtk.data import validate_series
from adtk.detector import PersistAD
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent import futures
import datetime
import asyncio
from flask import jsonify

import matplotlib.pyplot as plt
from adtk.visualization import plot
import seaborn as sns
from ScaleTest.requests_scale_test import TrendReqV2


state_list = [
    "AL",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY"
]


def get_key_word_trend(request):
    key_words = request.form.getlist('key_words')
    hours_in_trend = int(request.form.get('hours_in_trend'))
    return search_trend_by_keyword(key_words)


def get_daily_trend_values(data, anomalies, key_word, start_hour=36, end_hour=0):
    max_trends_dates = pd.to_datetime(data[pd.to_datetime(
        datetime.datetime.now() - datetime.timedelta(hours=start_hour)): pd.to_datetime(
        datetime.datetime.now() - datetime.timedelta(hours=end_hour))].idxmax())
    max_trends_dates = data[pd.to_datetime(max_trends_dates[0]) - datetime.timedelta(hours=1):pd.to_datetime(
        max_trends_dates[0])]
    trends = anomalies[anomalies[key_word].isnull() == False]
    trends = trends[trends[key_word] != 0]
    for trend_date in max_trends_dates.index.values:
        if trend_date in trends.index.values:
            return max_trends_dates[key_word].max()
    return 0


def get_monthly_trend_values(anomalies, key_word):
    return bool(anomalies[key_word].iloc[-1] >= 1)


def is_trend(kw_list, time_frame, geo='', window=2, debug=False):
    py_trend = TrendReqV2(hl='en-US', retries=2, timeout=None, backoff_factor=0.1)
    gts = py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
    gts = gts.drop(labels=['isPartial'], axis='columns', errors='ignore')
    # gts.at[gts.index[-1], kw_list[0]] = 80

    if gts.empty:
        return False, geo

    s = validate_series(gts)
    persist_ad = PersistAD(c=2.0, side='positive')
    try:
        # Number of dates data points to check
        persist_ad.window = window
        anomalies = persist_ad.fit_detect(s)
        is_monthly_trend = get_monthly_trend_values(anomalies, kw_list[0])
        print(f'is_monthly_trend {is_monthly_trend} geo {geo}')
        if debug:
            sns.set(color_codes=True)
            plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
            plt.title(geo + time_frame.replace('today', '').replace('now', ''))
        return is_monthly_trend, geo

    except Exception as e:
        print(f'Error in {kw_list[0]} geo {geo} {e}')
        return False, geo


def get_geo_tasks(executor, kw_list):
    tasks = []
    shuffle(state_list)
    for state in state_list:
        tasks.append(executor.submit(is_trend, kw_list, 'today 3-m', f'US-{state}', 7))
    return tasks


def create_tasks_func(kw_list):
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = get_geo_tasks(executor, kw_list)
        futures.wait(tasks, return_when=futures.ALL_COMPLETED)
        results = list(map(lambda x: x.result(), tasks))
        return results


def get_interest_over_time(kw_list, debug=False):
    if debug:
        result = [is_trend(kw_list, 'today 3-m', 'US', 7, debug)]
    else:
        result = create_tasks_func(kw_list)
    return result


def search_trend_by_keyword(key_word, debug=False):
    trends = get_interest_over_time(key_word, debug)

    found_trend = list(filter(lambda x: x[0], trends))
    if len(found_trend) > 0:
        print(f"key_word {key_word[0]} is trending in {found_trend}")
    else:
        print(f"key_word {key_word[0]} is not trending")

    # return jsonify(data)

