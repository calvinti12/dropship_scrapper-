# https://pypi.org/project/pytrends/#interest-by-region
from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
from adtk.data import validate_series
from adtk.detector import PersistAD
import seaborn as sns


def get_interest_over_time(kw_list):
    py_trend = TrendReq(hl='en-US', retries=2)
    get_all_trends(py_trend, kw_list)
    plt.show()


def get_trends(py_trend, kw_list, time_frame, geo='', window=2):
    py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
    sns.set(color_codes=True)
    gts = py_trend.interest_over_time()
    gts = gts.drop(labels=['isPartial'], axis='columns')
    s = validate_series(gts)
    persist_ad = PersistAD(c=2.0, side='positive')

    # Number of dates data points to check
    persist_ad.window = window
    anomalies = persist_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
    plt.title(geo + time_frame.replace('today', '').replace('now', ''))


def get_all_trends(py_trend, kw_list):
    # get_geo_trend(py_trend, kw_list, 'US')
    # get_geo_trend(py_trend, kw_list, 'CA')
    # get_geo_trend(py_trend, kw_list, 'GB')
    # get_geo_trend(py_trend, kw_list, 'AU')

    get_geo_trend(py_trend, kw_list, geo='')


def get_geo_trend(py_trend, kw_list, geo=''):
    get_trends(py_trend, kw_list, 'today 3-m', geo, 2), get_trends(py_trend, kw_list, 'now 7-d', geo, 8)


def get_historical_interest(kw_list, year_start, month_start, day_start, hour_start, year_end, month_end, day_end, hour_end, sleep):
    return TrendReq().get_historical_interest(kw_list, year_start=year_start, month_start=month_start, day_start=day_start, hour_start=hour_start, year_end=year_end, month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='', gprop='', sleep=sleep)