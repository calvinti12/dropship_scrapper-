import pytrends
from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
from adtk.visualization import plot
from adtk.detector import LevelShiftAD
from adtk.data import validate_series
from adtk.detector import PersistAD
from datetime import date, timedelta
import time
import seaborn as sns
# pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1)


def get_interest_over_time(kw_list):
    pytrend = TrendReq(hl='en-US', tz=360)
    pytrend.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='', gprop='')
    sns.set(color_codes=True)
    gts = pytrend.interest_over_time()
    gts = gts.drop(labels=['isPartial'], axis='columns')
    gts = gts.loc[gts.index < pd.to_datetime('2020-05-05')]
    s = validate_series(gts)
    persist_ad = PersistAD(c=2.0, side='positive')
    anomalies = persist_ad.fit_detect(s)
    plot(s, anomaly=anomalies, ts_linewidth=1, ts_markersize=5, anomaly_color='red')

    # level_shift_ad = LevelShiftAD(c=6.0, side='both', window=5)
    # data = gts.plot(figsize=(11, 8), title="Interest Over Time")
    # data.set_xlabel('Date')
    # data.set_ylabel('Trends Index')
    # data.tick_params(axis='both', which='major', labelsize=12)
    # anomalies = level_shift_ad.fit_detect(data)
    plt.show()

    # Immediately return a 200 response to the caller
    # # df_rm = pd.concat([diet.rolling(12).mean(), gym.rolling(12).mean()], axis=1)
    # dx = gts.mean().plot.line(figsize=(9, 6), title="Interest Over Time")
    # dx.set_xlabel('Date')
    # dx.set_ylabel('Trends Index')
    # dx.tick_params(axis='both', which='major', labelsize=12)





def get_historical_interest(kw_list, year_start, month_start, day_start, hour_start, year_end, month_end, day_end, hour_end, sleep):
    return TrendReq().get_historical_interest(kw_list, year_start=year_start, month_start=month_start, day_start=day_start, hour_start=hour_start, year_end=year_end, month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='', gprop='', sleep=sleep)