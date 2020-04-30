import pandas as pd                        
from pytrends.request import TrendReq
# pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1)
pytrend = TrendReq()


class GoogleTrends:
    def __init__(self, kw_list):
        pytrend.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')

    def get_interest_over_time(self):
        return pytrend.interest_over_time()


    def get_historical_interest(self, kw_list, year_start, month_start ,day_start ,hour_start,year_end,month_end,day_end,hour_end,sleep):
        return pytrend.get_historical_interest(kw_list, year_start=year_start, month_start=month_start, day_start=day_start, hour_start=hour_start, year_end=year_end, month_end=month_end, day_end=day_end, hour_end=hour_end, cat=0, geo='', gprop='', sleep=sleep)