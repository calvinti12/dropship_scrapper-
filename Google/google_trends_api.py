# https://pypi.org/project/pytrends/#interest-by-region
from pytrends.request import TrendReq
import pandas as pd
from adtk.data import validate_series
from adtk.detector import PersistAD
from concurrent import futures
import datetime
from flask import jsonify
# import matplotlib.pyplot as plt
# from adtk.visualization import plot
# import seaborn as sns


def get_interest_over_time(kw_list, hours_in_trend):
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', '', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'US', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'CA', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'GB', 5, hours_in_trend]),
                 executor.submit(lambda p: is_trend(*p), [kw_list, 'now 7-d', 'AU', 5, hours_in_trend])]

        futures.wait(tasks, timeout=70000, return_when=futures.ALL_COMPLETED)
    geo_trend = {
        '_Keyword': kw_list[0],
        'Worldwide': bool(tasks[0].result()),
        'United states': bool(tasks[1].result()),
        'Canada': bool(tasks[2].result()),
        'United kingdom': bool(tasks[3].result()),
        'Australia': bool(tasks[4].result())
    }
    return geo_trend


def get_interest_over_time_debug(kw_list, hours_in_trend):
    geo_trend = {
        '_Keyword': kw_list[0],
        'Worldwide': is_trend(kw_list, 'now 7-d', '', 5, hours_in_trend, True),
        'United states': is_trend(kw_list, 'now 7-d', 'US', 5, hours_in_trend, True),
        'Canada': is_trend(kw_list, 'now 7-d', 'CA', 5, hours_in_trend, True),
        'United kingdom': is_trend(kw_list, 'now 7-d', 'GB', 5, hours_in_trend, True),
        'Australia': is_trend(kw_list, 'now 7-d', 'AU', 5, hours_in_trend, True),
    }
    # plt.show()
    return geo_trend


def is_trend(kw_list, time_frame, geo='', window=2, hours_in_trend=4, debug=False):
    py_trend = TrendReq(hl='en-US', retries=3)
    py_trend.build_payload(kw_list, cat=0, timeframe=time_frame, geo=geo, gprop='')
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
    # if debug:
    #     sns.set(color_codes=True)
    #     plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')
    #     plt.title(geo + time_frame.replace('today', '').replace('now', ''))
    return trend_start.size > 0


def get_historical_interest(kw_list, year_start, month_start, day_start, hour_start, year_end, month_end, day_end,
                            hour_end, sleep):
    return TrendReq().get_historical_interest(kw_list, year_start=year_start, month_start=month_start,
                                              day_start=day_start, hour_start=hour_start, year_end=year_end,
                                              month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='',
                                              gprop='', sleep=sleep)


def get_key_word_trend(request):
    key_words = request.form.getlist('key_words')
    hours_in_trend = int(request.form.get('hours_in_trend'))
    max_workers = int(request.form.get('max_workers'))
    tasks = []
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for key_word in key_words:
            tasks.append(executor.submit(lambda p: get_interest_over_time(*p), [[key_word], hours_in_trend]))
    futures.wait(tasks, timeout=70000, return_when=futures.ALL_COMPLETED)
    map_iterator = list(map(lambda a: a.result(), tasks))

    # get_interest_over_time_debug(['Terry Crews'], hours_in_trend)
    return jsonify(map_iterator)
