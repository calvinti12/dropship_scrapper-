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


def get_key_word_trend(request):
    key_words = request.form.getlist('key_words')
    hours_in_trend = int(request.form.get('hours_in_trend'))
    google_trends_api = GoogleTrendsApi()
    return google_trends_api.search_trend_by_keyword(key_words, hours_in_trend)


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
    return bool(anomalies[key_word].iloc[-1] >=1)


class GoogleTrendsApi:
    def __init__(self):
        self.proxies_new = [
            "https://dropship:00005678@34.86.166.233:3128",
            "https://dropship:00005678@35.245.187.21:3128",
            "https://dropship:00005678@35.245.70.220:3128",
            "https://dropship:00005678@35.245.49.168:3128",
            "https://dropship:00005678@35.245.159.4:3128",
            "https://dropship:00005678@34.86.78.245:3128",
            "https://dropship:00005678@34.86.197.106:3128",
            "https://dropship:00005678@35.221.39.40:3128",
            "https://dropship:00005678@35.221.0.106:3128",
            "https://dropship:00005678@34.86.168.167:3128",
            "https://dropship:00005678@35.230.187.7:3128",
            "https://dropship:00005678@34.86.42.59:3128",
            "https://dropship:00005678@35.236.236.180:3128",
            "https://dropship:00005678@34.86.253.219:3128",
            "https://dropship:00005678@35.186.165.16:3128",
            "https://dropship:00005678@34.86.192.68:3128",
            "https://dropship:00005678@34.86.229.110:3128",
            "https://dropship:00005678@35.199.23.197:3128",
            "https://dropship:00005678@35.245.193.245:3128",
            "https://dropship:00005678@35.221.4.247:3128",
            "https://dropship:00005678@35.230.187.127:3128",
            "https://dropship:00005678@35.245.32.91:3128",
            "https://dropship:00005678@34.86.245.68:3128",
            "https://dropship:00005678@35.245.72.122:3128",
            "https://dropship:00005678@35.230.191.56:3128",
            "https://dropship:00005678@35.245.67.52:3128",
            "https://dropship:00005678@35.236.238.90:3128",
            "https://dropship:00005678@34.86.91.169:3128",
            "https://dropship:00005678@35.245.194.214:3128",
            "https://dropship:00005678@35.245.101.67:3128",
            "https://dropship:00005678@34.86.15.165:3128",
            "https://dropship:00005678@34.86.64.11:3128",
            "https://dropship:00005678@35.236.241.204:3128",
            "https://dropship:00005678@35.245.154.202:3128",
            "https://dropship:00005678@35.236.254.237:3128",
            "https://dropship:00005678@34.86.148.217:3128",
            "https://dropship:00005678@34.86.51.5:3128",
            "https://dropship:00005678@34.86.126.224:3128",
            "https://dropship:00005678@34.86.56.245:3128",
            "https://dropship:00005678@35.194.76.60:3128",
            "https://dropship:00005678@35.245.80.185:3128",
            "https://dropship:00005678@34.86.104.14:3128",
            "https://dropship:00005678@34.86.223.84:3128",
            "https://dropship:00005678@34.86.71.157:3128",
            "https://dropship:00005678@35.236.242.156:3128",
            "https://dropship:00005678@34.86.228.216:3128",
            "https://dropship:00005678@35.245.109.65:3128",
            "https://dropship:00005678@35.245.96.246:3128",
            "https://dropship:00005678@34.86.9.111:3128",
            "https://dropship:00005678@34.86.193.245:3128",
            "https://dropship:00005678@35.199.2.41:3128",
            "https://dropship:00005678@35.230.169.4:3128",
            "https://dropship:00005678@35.245.212.213:3128",
            "https://dropship:00005678@34.86.59.49:3128",
            "https://dropship:00005678@34.86.88.77:3128",
            "https://dropship:00005678@34.86.239.177:3128",
            "https://dropship:00005678@34.86.170.7:3128",
            "https://dropship:00005678@35.230.185.198:3128",
            "https://dropship:00005678@35.245.124.191:3128",
            "https://dropship:00005678@35.199.23.45:3128",
            "https://dropship:00005678@34.86.214.48:3128",
            "https://dropship:00005678@34.86.124.12:3128",
            "https://dropship:00005678@34.86.50.233:3128",
            "https://dropship:00005678@35.236.207.120:3128",
            "https://dropship:00005678@34.86.123.231:3128",
            "https://dropship:00005678@34.86.221.234:3128",
            "https://dropship:00005678@35.245.53.194:3128",
            "https://dropship:00005678@34.86.192.18:3128",
            "https://dropship:00005678@34.86.61.22:3128"
        ]
        shuffle(self.proxies_new)
        self.py_trend = TrendReqV2(hl='en-US', proxies=self.proxies_new, retries=5, timeout=None, backoff_factor=0.3, )

    def create_tasks_func(self, kw_list, hours_in_trend):
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            tasks = self.get_geo_tasks(executor, kw_list, hours_in_trend)
            futures.wait(tasks, return_when=futures.ALL_COMPLETED)
            results = list(map(lambda x: x.result(), tasks))
            return results

    def get_interest_over_time(self, kw_list, hours_in_trend, debug=False):
        if debug:
            result = [self.is_trend(kw_list, 'today 3-m', 'US', 5, hours_in_trend, debug)]
        else:
            result = self.create_tasks_func(kw_list, hours_in_trend)
        return result

    def is_trend(self, kw_list, time_frame, geo='', window=2, hours_in_trend=36, debug=False):
        try:
            gts = self.py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
            gts = gts.drop(labels=['isPartial'], axis='columns', errors='ignore')
            # gts.at[gts.index[-1], kw_list[0]] = 80

            if gts.empty: return False
            s = validate_series(gts)
            persist_ad = PersistAD(c=2.0, side='positive')

            # Number of dates data points to check
            persist_ad.window = window
            anomalies = persist_ad.fit_detect(s)
            is_monthly_trend = get_monthly_trend_values(anomalies, kw_list[0])
            if debug:
                sns.set(color_codes=True)
                plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
                plt.title(geo + time_frame.replace('today', '').replace('now', ''))
            return is_monthly_trend, geo

        except Exception as e:
            print(f'Error in {kw_list[0]} geo {geo} {e}')
            return False, geo

    def search_trend_by_keyword(self, key_words, hours_in_trend, debug=False):
        for key_word in key_words:
            trends = self.get_interest_over_time([key_word], hours_in_trend, debug)

            found_trend = list(filter(lambda x: x[0], trends))
            if len(found_trend) > 0:
                print(f"key_word {key_word} is trending in {found_trend[1]}")
            else:
                print(f"key_word {key_word} is not trending")

        # return jsonify(data)

    def get_geo_tasks(self, executor, kw_list, hours_in_trend):
        state_list = [
            "AL",
            "AK",
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
        tasks = []
        for state in state_list:
            tasks.append(executor.submit(self.is_trend, kw_list, 'today 3-m', f'US-{state}', 5, hours_in_trend))
        return tasks
