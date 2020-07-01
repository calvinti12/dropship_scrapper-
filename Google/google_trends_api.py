# https://pypi.org/project/pytrends/#interest-by-region
from pytrends.request import TrendReq
import pandas as pd
from adtk.data import validate_series
from adtk.detector import PersistAD
from concurrent import futures
import datetime
# import matplotlib.pyplot as plt
# from adtk.visualization import plot
# import seaborn as sns


def get_interest_over_time(kw_list, hours_in_trend):
    return get_all_trends(kw_list, hours_in_trend)
    # plt.show()


def get_all_trends(kw_list, hours_in_trend):

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', '', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'US', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'CA', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'GB', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'AU', 5, hours_in_trend])]

        futures.wait(tasks, timeout=70000, return_when=futures.ALL_COMPLETED)
    geo_trend = {
        'Worldwide': tasks[0].result(),
        'United states': tasks[1].result(),
        'Canada': tasks[2].result(),
        'United kingdom': tasks[3].result(),
        'Australia': tasks[4].result(),
        'update': datetime.datetime.now()
    }
    return geo_trend


def is_trend(kw_list, time_frame, geo='', window=2, hours_in_trend=4):
    py_trend = TrendReq(hl='en-US', retries=3)
    py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
    # sns.set(color_codes=True)
    gts = py_trend.interest_over_time()
    gts = gts.drop(labels=['isPartial'], axis='columns')
    s = validate_series(gts)
    persist_ad = PersistAD(c=2.0, side='positive')

    # Number of dates data points to check
    persist_ad.window = window
    anomalies = persist_ad.fit_detect(s)
    trend_start = anomalies[anomalies[kw_list[0]].isnull() == False]
    trend_start = trend_start[trend_start[kw_list[0]] != 0]
    trend_start = trend_start.loc[trend_start.index > pd.to_datetime(datetime.datetime.now() - datetime.timedelta(hours=hours_in_trend))]
    print(trend_start.size)
    # plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
    # plt.title(geo + time_frame.replace('today', '').replace('now', ''))
    return trend_start.size > 0


def get_historical_interest(kw_list, year_start, month_start, day_start, hour_start, year_end, month_end, day_end,
                            hour_end, sleep):
    return TrendReq().get_historical_interest(kw_list, year_start=year_start, month_start=month_start,
                                              day_start=day_start, hour_start=hour_start, year_end=year_end,
                                              month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='',
                                              gprop='', sleep=sleep)
