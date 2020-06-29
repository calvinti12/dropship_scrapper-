import pytrends
from pytrends.request import TrendReq
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
# pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1)


def get_interest_over_time(kw_list):
    pytrend = TrendReq(hl='en-US', tz=360)
    pytrend.build_payload(kw_list, cat=0, timeframe='today 3-m', geo='', gprop='')
    gts = pytrend.interest_over_time()
    # Immediately return a 200 response to the caller
    sns.set(color_codes=True)
    df_rm = []
    for item in kw_list:
        df_rm = df_rm.concat([gts[item].rolling(12).mean()], axis=1)
    dx = df_rm.plot(figsize=(20, 10), linewidth=5, fontsize=20)
    # dx = gts.mean().plot.line(figsize=(9, 6), title="Interest Over Time")
    dx.set_xlabel('Date')
    dx.set_ylabel('Trends Index')
    dx.tick_params(axis='both', which='major', labelsize=12)
    print(gts.head())
    plt.show()



def get_historical_interest(kw_list, year_start, month_start, day_start, hour_start, year_end, month_end, day_end, hour_end, sleep):
    return TrendReq().get_historical_interest(kw_list, year_start=year_start, month_start=month_start, day_start=day_start, hour_start=hour_start, year_end=year_end, month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='', gprop='', sleep=sleep)