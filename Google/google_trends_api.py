# https://pypi.org/project/pytrends/#interest-by-region
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

proxies = {
    '': [
        "https://dropship:00005678@34.86.126.224:3128"
    ],
    'US': [
        "https://dropship:00005678@35.245.80.185:3128",
        "https://dropship:00005678@34.86.104.14:3128"
    ],
    'CA': [
        "https://dropship:00005678@34.86.71.157:3128",
        "https://dropship:00005678@35.245.96.246:3128"
    ],
    'GB': [
        "https://dropship:00005678@34.86.170.7:3128",
        "https://dropship:00005678@35.245.49.168:3128"
    ],
    'AU': [
        "https://dropship:00005678@35.245.194.214:3128",
        "https://dropship:00005678@34.86.229.110:3128"
    ],
}


def create_tasks_func(kw_list, hours_in_trend):
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            executor.submit(is_trend, kw_list, 'now 7-d', '', 5, hours_in_trend),
            executor.submit(is_trend, kw_list, 'now 7-d', 'US', 5, hours_in_trend),
            executor.submit(is_trend, kw_list, 'now 7-d', 'CA', 5, hours_in_trend),
            executor.submit(is_trend, kw_list, 'now 7-d', 'GB', 5, hours_in_trend),
            executor.submit(is_trend, kw_list, 'now 7-d', 'AU', 5, hours_in_trend)
        ]

        futures.wait(tasks, timeout=70000, return_when=futures.ALL_COMPLETED)
        results = list(map(lambda x: x.result(), tasks))
        return results


def get_interest_over_time(kw_list, hours_in_trend, debug=False):
    if debug:
        result = is_trend(kw_list, 'now 7-d', 'CA', 5, hours_in_trend, debug=debug)
    else:
        result = create_tasks_func(kw_list, hours_in_trend)

    geo_trend = [{'Geo': 'Worldwide', 'is_trend': bool(result[0])},
                 {'Geo': 'United states', 'is_trend': bool(result[1])},
                 {'Geo': 'Canada', 'is_trend': bool(result[2])},
                 {'Geo': 'United kingdom', 'is_trend': bool(result[3])},
                 {'Geo': 'Australia', 'is_trend': bool(result[4])}]
    return geo_trend


def is_trend(kw_list, time_frame, geo='', window=2, hours_in_trend=36, debug=False):
    try:
        py_trend = TrendReq(hl='en-US', proxies=proxies[geo], retries=5, timeout=None, backoff_factor=0.3,)
        py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
        gts = py_trend.interest_over_time()
        gts = gts.drop(labels=['isPartial'], axis='columns', errors='ignore')
        if gts.empty: return False
        s = validate_series(gts)
        persist_ad = PersistAD(c=2.0, side='positive')

        # Number of dates data points to check
        persist_ad.window = window
        anomalies = persist_ad.fit_detect(s)
        trend_start = get_trend_values(s, anomalies, kw_list[0], start_hour=hours_in_trend, end_hour=12)
        current_trend = get_trend_values(s, anomalies, kw_list[0], start_hour=11, end_hour=0)
        if debug:
            sns.set(color_codes=True)
            plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
            plt.title(geo + time_frame.replace('today', '').replace('now', ''))
        return current_trend > trend_start > 0

    except Exception as e:
        print(f'Error in {kw_list[0]} geo {geo} {e}')
        return False


def get_trend_values(data, anomalies, key_word, start_hour=36, end_hour=0):
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


def search_trend_by_keyword(key_words, hours_in_trend, debug=False):
    for key_word in key_words:
        trends = get_interest_over_time([key_word], hours_in_trend, debug)
        found_trend = list(filter(lambda x: x['is_trend'], trends))
        if len(found_trend) > 0:
            print(f"key_word {key_word} is trending in {found_trend}")

    # return jsonify(data)


def get_key_word_trend(request):
    key_words = request.form.getlist('key_words')
    hours_in_trend = int(request.form.get('hours_in_trend'))
    return search_trend_by_keyword(key_words, hours_in_trend)
