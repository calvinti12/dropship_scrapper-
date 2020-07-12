# https://pypi.org/project/pytrends/#interest-by-region
import json
import random
from random import shuffle
import requests
import pandas as pd
from adtk.data import validate_series
from adtk.detector import PersistAD
from concurrent import futures
import datetime

# import matplotlib.pyplot as plt
# from adtk.visualization import plot
# import seaborn as sns
from flask import jsonify
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

state_list = [
    "CA",
    "TX",
    "NY",
    "FL"
]


def get_key_word_trend(request):
    key_words = request.form.getlist('key_words')
    tasks = []
    with futures.ThreadPoolExecutor(max_workers=None) as executor:
        for key_word in key_words:
            tasks.append(executor.submit(lambda p: search_trend_by_keyword(*p), [key_word, False]))
        futures.wait(tasks, return_when=futures.ALL_COMPLETED)
        results = list(map(lambda a: a.result(), tasks))
        print(f'Results {results}')
        return jsonify(results)


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


def get_is_monthly_trend_values(gts, anomalies, key_word):
    is_trend_by_anomaly = bool(anomalies[key_word].iloc[-1] >= 1)
    is_low_search_volumes = False
    number_of_zero_searches = gts.groupby(key_word).size().get(key=0)
    if number_of_zero_searches:
        is_low_search_volumes = bool(number_of_zero_searches > 55)
    return is_trend_by_anomaly and is_low_search_volumes is False


def is_trend(key_word, time_frame, geo='', window=7, debug=False):
    py_trend = TrendReqV2(retries=2, geo=geo)
    gts = py_trend.get_key_word_trend(key_word, time_frame)
    # gts.at[gts.index[-1], key_word] = 100

    if gts.empty:
        return False, geo

    s = validate_series(gts)
    persist_ad = PersistAD(c=2.0, side='positive')
    try:
        # Number of dates data points to check
        persist_ad.window = window
        anomalies = persist_ad.fit_detect(s)
        is_monthly_trend = get_is_monthly_trend_values(gts, anomalies, key_word)
        # if debug:
        #     sns.set(color_codes=True)
        #     plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
        #     plt.title(geo + time_frame.replace('today', '').replace('now', ''))
        return is_monthly_trend, geo

    except Exception as e:
        print(f'Error in {key_word} geo {geo} {e}')
        return False, geo


def get_geo_tasks(executor, key_word):
    tasks = []
    for state in state_list:
        tasks.append(executor.submit(is_trend, key_word, 'today 3-m', f'US-{state}', 7))
    tasks.append(executor.submit(is_trend, key_word, 'today 3-m', f'US', 7))
    return tasks


def create_tasks_func(key_word):
    with futures.ThreadPoolExecutor(max_workers=len(state_list) + 1) as executor:
        tasks = get_geo_tasks(executor, key_word)
        futures.wait(tasks, return_when=futures.ALL_COMPLETED)
        results = list(map(lambda x: x.result(), tasks))
        return results


def create_func(key_word):
    tasks = [is_trend(key_word, 'today 3-m', 'US', 7)]
    for state in state_list:
        tasks.append(is_trend(key_word, 'today 3-m', f'US-{state}', 7))
    return tasks


def get_interest_over_time(key_word, debug=False):
    if debug:
        result = [is_trend(key_word, 'today 3-m', 'US', 7, debug)]
    else:
        result = create_func(key_word)
    return result


def search_trend_by_keyword(key_word):
    trends = get_interest_over_time(key_word, False)
    found_trend = list(filter(lambda x: x[0], trends))
    if len(found_trend) > 0:
        print(f"key_word {key_word} is trending in {found_trend}")
        found_trend = list(map(lambda x: x[1], found_trend))
    else:
        print(f"key_word {key_word} is not trending")

    return {'key_word': key_word, 'geo': found_trend}


class TrendReqV2:
    """
    Google Trends API
    """
    GET_METHOD = 'get'
    POST_METHOD = 'post'
    GENERAL_URL = 'https://trends.google.com/trends/api/explore'
    INTEREST_OVER_TIME_URL = 'https://trends.google.com/trends/api/widgetdata/multiline'

    proxies_group_1 = [
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
    proxies_group_2 = [
        "https://dropship:00005678@35.231.53.56:3128",
        "https://dropship:00005678@35.237.243.160:3128",
        "https://dropship:00005678@35.185.32.38:3128",
        "https://dropship:00005678@35.231.184.121:3128",
        "https://dropship:00005678@104.196.106.155:3128",
        "https://dropship:00005678@34.74.241.83:3128",
        "https://dropship:00005678@34.75.75.120:3128",
        "https://dropship:00005678@34.75.78.3:3128",
        "https://dropship:00005678@34.75.72.89:3128",
        "https://dropship:00005678@34.74.99.77:3128",
        "https://dropship:00005678@34.74.183.40:3128",
        "https://dropship:00005678@34.73.250.172:3128",
        "https://dropship:00005678@34.74.205.197:3128",
        "https://dropship:00005678@34.75.141.165:3128",
        "https://dropship:00005678@34.73.126.254:3128",
        "https://dropship:00005678@35.243.243.145:3128",
        "https://dropship:00005678@35.196.79.100:3128",
        "https://dropship:00005678@34.73.238.238:3128",
        "https://dropship:00005678@35.227.113.253:3128",
        "https://dropship:00005678@35.231.219.141:3128",
        "https://dropship:00005678@34.74.151.227:3128",
        "https://dropship:00005678@35.196.75.25:3128",
        "https://dropship:00005678@34.75.237.232:3128",
        "https://dropship:00005678@35.196.153.10:3128",
        "https://dropship:00005678@34.73.10.206:3128",
        "https://dropship:00005678@34.73.204.204:3128",
        "https://dropship:00005678@34.75.82.155:3128",
        "https://dropship:00005678@34.74.16.118:3128",
        "https://dropship:00005678@35.237.245.155:3128",
        "https://dropship:00005678@35.231.172.72:3128",
        "https://dropship:00005678@35.237.65.178:3128",
        "https://dropship:00005678@35.231.164.135:3128",
        "https://dropship:00005678@34.75.211.62:3128",
        "https://dropship:00005678@34.74.114.132:3128",
        "https://dropship:00005678@35.229.72.43:3128",
        "https://dropship:00005678@35.190.142.192:3128",
        "https://dropship:00005678@104.196.107.69:3128",
        "https://dropship:00005678@104.196.144.142:3128",
        "https://dropship:00005678@104.196.65.233:3128",
        "https://dropship:00005678@35.231.19.81:3128",
        "https://dropship:00005678@34.75.171.127:3128",
        "https://dropship:00005678@34.73.226.89:3128",
        "https://dropship:00005678@35.243.211.68:3128",
        "https://dropship:00005678@35.231.247.145:3128",
        "https://dropship:00005678@34.75.242.60:3128",
        "https://dropship:00005678@35.237.23.145:3128",
        "https://dropship:00005678@35.190.164.7:3128",
        "https://dropship:00005678@35.185.77.44:3128",
        "https://dropship:00005678@35.227.42.102:3128",
        "https://dropship:00005678@35.185.27.111:3128",
        "https://dropship:00005678@35.231.93.179:3128",
        "https://dropship:00005678@34.74.235.243:3128",
        "https://dropship:00005678@34.74.47.77:3128",
        "https://dropship:00005678@35.196.199.140:3128",
        "https://dropship:00005678@34.74.103.185:3128",
        "https://dropship:00005678@35.196.139.49:3128",
        "https://dropship:00005678@104.196.160.27:3128",
        "https://dropship:00005678@35.243.165.131:3128",
        "https://dropship:00005678@35.237.215.51:3128",
        "https://dropship:00005678@34.75.6.212:3128",
        "https://dropship:00005678@35.237.206.124:3128",
        "https://dropship:00005678@34.75.170.102:3128",
        "https://dropship:00005678@34.73.219.138:3128",
        "https://dropship:00005678@35.227.99.206:3128",
        "https://dropship:00005678@35.185.68.127:3128",
        "https://dropship:00005678@104.196.143.112:3128",
        "https://dropship:00005678@35.190.150.187:3128",
        "https://dropship:00005678@35.243.221.164:3128",
        "https://dropship:00005678@35.229.56.183:3128"
    ]
    proxies_group_3 = [
        "https://dropship:00005678@34.69.62.199:3128",
        "https://dropship:00005678@35.224.60.241:3128",
        "https://dropship:00005678@35.222.33.254:3128",
        "https://dropship:00005678@35.226.27.21:3128",
        "https://dropship:00005678@35.232.226.36:3128",
        "https://dropship:00005678@35.194.32.201:3128",
        "https://dropship:00005678@35.224.193.254:3128",
        "https://dropship:00005678@146.148.33.52:3128",
        "https://dropship:00005678@34.69.227.122:3128",
        "https://dropship:00005678@35.238.213.71:3128",
        "https://dropship:00005678@104.197.47.3:3128",
        "https://dropship:00005678@104.197.201.255:3128",
        "https://dropship:00005678@34.69.151.93:3128",
        "https://dropship:00005678@35.238.219.175:3128",
        "https://dropship:00005678@34.66.59.214:3128",
        "https://dropship:00005678@35.193.115.100:3128",
        "https://dropship:00005678@35.194.43.247:3128",
        "https://dropship:00005678@34.72.166.31:3128",
        "https://dropship:00005678@104.197.174.22:3128",
        "https://dropship:00005678@34.67.47.81:3128",
        "https://dropship:00005678@35.225.144.122:3128",
        "https://dropship:00005678@34.69.110.56:3128",
        "https://dropship:00005678@35.238.65.115:3128",
        "https://dropship:00005678@35.239.114.13:3128",
        "https://dropship:00005678@34.71.84.244:3128",
        "https://dropship:00005678@35.222.183.209:3128",
        "https://dropship:00005678@34.72.126.221:3128",
        "https://dropship:00005678@35.223.94.17:3128",
        "https://dropship:00005678@35.188.195.229:3128",
        "https://dropship:00005678@34.67.138.175:3128",
        "https://dropship:00005678@35.184.74.242:3128",
        "https://dropship:00005678@35.226.234.240:3128",
        "https://dropship:00005678@35.222.171.66:3128",
        "https://dropship:00005678@104.198.132.198:3128",
        "https://dropship:00005678@35.222.82.109:3128",
        "https://dropship:00005678@35.238.183.121:3128",
        "https://dropship:00005678@34.70.198.23:3128",
        "https://dropship:00005678@34.72.145.80:3128",
        "https://dropship:00005678@34.70.237.119:3128",
        "https://dropship:00005678@34.71.242.123:3128",
        "https://dropship:00005678@34.72.110.60:3128",
        "https://dropship:00005678@35.188.83.147:3128",
        "https://dropship:00005678@35.232.105.44:3128",
        "https://dropship:00005678@34.67.232.51:3128",
        "https://dropship:00005678@34.69.92.3:3128",
        "https://dropship:00005678@35.226.37.111:3128",
        "https://dropship:00005678@35.184.249.190:3128",
        "https://dropship:00005678@35.202.79.228:3128",
        "https://dropship:00005678@35.224.164.252:3128",
        "https://dropship:00005678@35.222.208.41:3128",
        "https://dropship:00005678@35.232.99.222:3128",
        "https://dropship:00005678@35.202.210.136:3128",
        "https://dropship:00005678@34.67.184.156:3128",
        "https://dropship:00005678@34.72.18.103:3128",
        "https://dropship:00005678@34.67.235.116:3128",
        "https://dropship:00005678@35.223.52.169:3128",
        "https://dropship:00005678@34.71.249.105:3128",
        "https://dropship:00005678@35.224.62.141:3128",
        "https://dropship:00005678@34.69.95.53:3128",
        "https://dropship:00005678@35.193.35.73:3128",
        "https://dropship:00005678@35.193.170.251:3128",
        "https://dropship:00005678@34.70.119.215:3128",
        "https://dropship:00005678@35.226.232.235:3128",
        "https://dropship:00005678@35.226.86.115:3128",
        "https://dropship:00005678@34.72.89.167:3128",
        "https://dropship:00005678@35.226.7.210:3128",
        "https://dropship:00005678@35.224.150.10:3128",
        "https://dropship:00005678@35.226.137.136:3128",
        "https://dropship:00005678@104.154.185.31:3128"
    ]
    proxies_group_4 = [
        "https://dropship:00005678@34.69.62.199:3128",
        "https://dropship:00005678@35.224.60.241:3128",
        "https://dropship:00005678@35.222.33.254:3128",
        "https://dropship:00005678@35.226.27.21:3128",
        "https://dropship:00005678@35.232.226.36:3128",
        "https://dropship:00005678@35.194.32.201:3128",
        "https://dropship:00005678@35.224.193.254:3128",
        "https://dropship:00005678@146.148.33.52:3128",
        "https://dropship:00005678@34.69.227.122:3128",
        "https://dropship:00005678@35.238.213.71:3128",
        "https://dropship:00005678@104.197.47.3:3128",
        "https://dropship:00005678@104.197.201.255:3128",
        "https://dropship:00005678@34.69.151.93:3128",
        "https://dropship:00005678@35.238.219.175:3128",
        "https://dropship:00005678@34.66.59.214:3128",
        "https://dropship:00005678@35.193.115.100:3128",
        "https://dropship:00005678@35.194.43.247:3128",
        "https://dropship:00005678@34.72.166.31:3128",
        "https://dropship:00005678@104.197.174.22:3128",
        "https://dropship:00005678@34.67.47.81:3128",
        "https://dropship:00005678@35.225.144.122:3128",
        "https://dropship:00005678@34.69.110.56:3128",
        "https://dropship:00005678@35.238.65.115:3128",
        "https://dropship:00005678@35.239.114.13:3128",
        "https://dropship:00005678@34.71.84.244:3128",
        "https://dropship:00005678@35.222.183.209:3128",
        "https://dropship:00005678@34.72.126.221:3128",
        "https://dropship:00005678@35.223.94.17:3128",
        "https://dropship:00005678@35.188.195.229:3128",
        "https://dropship:00005678@34.67.138.175:3128",
        "https://dropship:00005678@35.184.74.242:3128",
        "https://dropship:00005678@35.226.234.240:3128",
        "https://dropship:00005678@35.222.171.66:3128",
        "https://dropship:00005678@104.198.132.198:3128",
        "https://dropship:00005678@35.222.82.109:3128",
        "https://dropship:00005678@35.238.183.121:3128",
        "https://dropship:00005678@34.70.198.23:3128",
        "https://dropship:00005678@34.72.145.80:3128",
        "https://dropship:00005678@34.70.237.119:3128",
        "https://dropship:00005678@34.71.242.123:3128",
        "https://dropship:00005678@34.72.110.60:3128",
        "https://dropship:00005678@35.188.83.147:3128",
        "https://dropship:00005678@35.232.105.44:3128",
        "https://dropship:00005678@34.67.232.51:3128",
        "https://dropship:00005678@34.69.92.3:3128",
        "https://dropship:00005678@35.226.37.111:3128",
        "https://dropship:00005678@35.184.249.190:3128",
        "https://dropship:00005678@35.202.79.228:3128",
        "https://dropship:00005678@35.224.164.252:3128",
        "https://dropship:00005678@35.222.208.41:3128",
        "https://dropship:00005678@35.232.99.222:3128",
        "https://dropship:00005678@35.202.210.136:3128",
        "https://dropship:00005678@34.67.184.156:3128",
        "https://dropship:00005678@34.72.18.103:3128",
        "https://dropship:00005678@34.67.235.116:3128",
        "https://dropship:00005678@35.223.52.169:3128",
        "https://dropship:00005678@34.71.249.105:3128",
        "https://dropship:00005678@35.224.62.141:3128",
        "https://dropship:00005678@34.69.95.53:3128",
        "https://dropship:00005678@35.193.35.73:3128",
        "https://dropship:00005678@35.193.170.251:3128",
        "https://dropship:00005678@34.70.119.215:3128",
        "https://dropship:00005678@35.226.232.235:3128",
        "https://dropship:00005678@35.226.86.115:3128",
        "https://dropship:00005678@34.72.89.167:3128",
        "https://dropship:00005678@35.226.7.210:3128",
        "https://dropship:00005678@35.224.150.10:3128",
        "https://dropship:00005678@35.226.137.136:3128",
        "https://dropship:00005678@104.154.185.31:3128"
    ]

    def __init__(self, retries=0, geo=''):
        """
        Initialize default values for params
        """
        # google rate limit
        self.google_rl = 'You have reached your quota limit. Please try again later.'
        self.results = None
        # set user defined options used globally
        self.tz = 360
        self.hl = 'en-US'
        self.geo = geo
        self.key_word = None
        self.cookies = None
        self.timeout = None
        self.timeframe = 'today 5-y'
        self.proxies_group_us = TrendReqV2.proxies_group_1[len(TrendReqV2.proxies_group_1) - 14:]
        self.proxies_group_us.append(TrendReqV2.proxies_group_2[len(TrendReqV2.proxies_group_2) - 14:])
        self.proxies_group_us.append(TrendReqV2.proxies_group_3[len(TrendReqV2.proxies_group_3) - 14:])
        self.proxies_group_us.append(TrendReqV2.proxies_group_4[len(TrendReqV2.proxies_group_4) - 14:])
        self.proxies_group_general = {
            'US-CA': TrendReqV2.proxies_group_1[:len(TrendReqV2.proxies_group_1) - 14],
            'US-TX': TrendReqV2.proxies_group_2[:len(TrendReqV2.proxies_group_2) - 14],
            'US-NY': TrendReqV2.proxies_group_3[:len(TrendReqV2.proxies_group_3) - 14],
            'US-FL': TrendReqV2.proxies_group_4[:len(TrendReqV2.proxies_group_4) - 14],
            'US': self.proxies_group_us
        }
        self.proxy_index = random.randint(0, len(self.proxies_group_general[self.geo]) - 1)
        self.proxies = self.proxies_group_general[self.geo]  # add a proxy option
        shuffle(self.proxies)
        self.current_proxy = {'https': self.proxies[self.proxy_index]}  # add a proxy option
        self.retries = retries
        self.backoff_factor = 0.1
        self.requests_args = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'accept-language': self.hl
        }
        self.cookies = self.get_working_proxy()
        # intialize widget payloads
        self.token_payload = dict()
        self.interest_over_time_widget = dict()

    def get_key_word_trend(self, key_word, timeframe):
        """Create the payload for related queries, interest over time and interest by region"""
        self.key_word = key_word
        self.timeframe = timeframe
        self.token_payload = {
            'hl': self.hl,
            'tz': self.tz,
            'req': {'comparisonItem': [], 'category': 0, 'property': ''}
        }

        # build out json for each keyword
        keyword_payload = {'keyword': key_word, 'time': timeframe,
                           'geo': self.geo}
        self.token_payload['req']['comparisonItem'].append(keyword_payload)
        # requests will mangle this if it is not a string
        self.token_payload['req'] = json.dumps(self.token_payload['req'])
        # get tokens
        self.get_token()
        results = self.interest_over_time()
        return results

    def get_working_proxy(self):
        """
        Gets google cookie (used for each and every proxy; once on init otherwise)
        Removes proxy from the list on proxy error
        """
        while True:
            try:
                return dict(filter(lambda i: i[0] == 'NID', requests.get(
                    'https://trends.google.com/?geo={geo}'.format(
                        geo=self.hl[-2:]),
                    timeout=self.timeout,
                    proxies=self.current_proxy,
                    **self.requests_args
                ).cookies.items()))
            except requests.exceptions.ProxyError:
                print(f"Error in proxy {self.current_proxy}")
                self.next_proxy()

    def next_proxy(self):
        """
        Increment proxy INDEX; zero on overflow
        """
        if self.proxy_index < (len(self.proxies) - 1):
            self.proxy_index += 1
        else:
            self.proxy_index = 0
        self.current_proxy = {'https': self.proxies[self.proxy_index]}

    def get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        """Send a request to Google and return the JSON response as a Python object
        :param url: the url to which the request will be sent
        :param method: the HTTP method ('get' or 'post')
        :param trim_chars: how many characters should be trimmed off the beginning of the content of the response
            before this is passed to the JSON parser
        :param kwargs: any extra key arguments passed to the request builder (usually query parameters or data)
        :return:
        """
        s = requests.session()
        # Retries mechanism. Activated when one of statements >0 (best used for proxy)
        if self.retries > 0 or self.backoff_factor > 0:
            retry = Retry(total=self.retries, read=self.retries,
                          connect=self.retries,
                          backoff_factor=self.backoff_factor)
            s.mount('https://', HTTPAdapter(max_retries=retry))
        if method == TrendReqV2.POST_METHOD:
            response = s.post(url, timeout=self.timeout, headers=self.headers,
                              proxies=self.current_proxy,
                              cookies=self.cookies, **kwargs,
                              **self.requests_args)  # DO NOT USE retries or backoff_factor here
        else:
            response = s.get(url, timeout=self.timeout, headers=self.headers,
                             cookies=self.cookies,
                             proxies=self.current_proxy,
                             **kwargs, **self.requests_args)  # DO NOT USE retries or backoff_factor here
        # check if the response contains json and throw an exception otherwise
        # Google mostly sends 'application/json' in the Content-Type header,
        # but occasionally it sends 'application/javascript
        # and sometimes even 'text/javascript
        if response.status_code == 200 and 'application/json' in \
                response.headers['Content-Type'] or \
                'application/javascript' in response.headers['Content-Type'] or \
                'text/javascript' in response.headers['Content-Type']:
            # trim initial characters
            # some responses start with garbage characters, like ")]}',"
            # these have to be cleaned before being passed to the json parser
            content = response.text[trim_chars:]
            # parse json
            return json.loads(content)
        else:
            # error
            print(f'The request failed: code {response.status_code}. proxy {self.current_proxy}')
            self.retry_key_word()

    def retry_key_word(self):
        self.cookies = self.get_working_proxy()
        self.get_key_word_trend(self.key_word, self.timeframe)

    def get_token(self):
        """Makes request to Google to get API tokens for interest over time, interest by region and related queries"""
        # make the request and parse the returned json
        widget_dict = self.get_data(
            url=TrendReqV2.GENERAL_URL,
            method=TrendReqV2.GET_METHOD,
            params=self.token_payload,
            trim_chars=4,
        )['widgets']
        # order of the json matters...
        # clear self.related_queries_widget_list and self.related_topics_widget_list
        # of old keywords'widgets
        # assign requests
        for widget in widget_dict:
            if widget['id'] == 'TIMESERIES':
                self.interest_over_time_widget = widget
        return

    def interest_over_time(self):
        """Request data from Google's Interest Over Time section and return a dataframe"""

        over_time_payload = {
            # convert to string as requests will mangle
            'req': json.dumps(self.interest_over_time_widget['request']),
            'token': self.interest_over_time_widget['token'],
            'tz': self.tz
        }

        # make the request and parse the returned json
        req_json = self.get_data(
            url=TrendReqV2.INTEREST_OVER_TIME_URL,
            method=TrendReqV2.GET_METHOD,
            trim_chars=5,
            params=over_time_payload,
        )

        df = pd.DataFrame(req_json['default']['timelineData'])
        if (df.empty):
            return df

        df['date'] = pd.to_datetime(df['time'].astype(dtype='float64'),
                                    unit='s')
        df = df.set_index(['date']).sort_index()
        # split list columns into seperate ones, remove brackets and split on comma
        result_df = df['value'].apply(lambda x: pd.Series(
            str(x).replace('[', '').replace(']', '').split(',')))
        # rename each column with its search term, relying on order that google provides...
        result_df.insert(len(result_df.columns), self.key_word,
                         result_df[0].astype('int'))
        del result_df[0]

        final = result_df
        return final