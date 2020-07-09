from __future__ import absolute_import, print_function, unicode_literals
import json
import pandas as pd
from fake_useragent import UserAgent
from random import shuffle
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pytrends import exceptions

proxies_new = [
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


class TrendReqV2:
    """
    Google Trends API
    """
    GET_METHOD = 'get'
    POST_METHOD = 'post'
    GENERAL_URL = 'https://trends.google.com/trends/api/explore'
    INTEREST_OVER_TIME_URL = 'https://trends.google.com/trends/api/widgetdata/multiline'
    INTEREST_BY_REGION_URL = 'https://trends.google.com/trends/api/widgetdata/comparedgeo'
    RELATED_QUERIES_URL = 'https://trends.google.com/trends/api/widgetdata/relatedsearches'
    TRENDING_SEARCHES_URL = 'https://trends.google.com/trends/hottrends/visualize/internal/data'
    TOP_CHARTS_URL = 'https://trends.google.com/trends/api/topcharts'
    SUGGESTIONS_URL = 'https://trends.google.com/trends/api/autocomplete/'
    CATEGORIES_URL = 'https://trends.google.com/trends/api/explore/pickers/category'
    TODAY_SEARCHES_URL = 'https://trends.google.com/trends/api/dailytrends'

    def __init__(self, hl='en-US', tz=360, geo='', timeout=None,
                 retries=0, backoff_factor=0, requests_args=None):
        """
        Initialize default values for params
        """
        # google rate limit
        self.google_rl = 'You have reached your quota limit. Please try again later.'
        self.results = None
        # set user defined options used globally
        self.tz = tz
        self.hl = hl
        self.geo = geo
        self.kw_list = list()
        self.timeout = timeout

        shuffle(proxies_new)

        self.proxies = proxies_new  # add a proxy option
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.requests_args = requests_args or {}
        self.cookies = self.GetGoogleCookie()
        # intialize widget payloads
        self.token_payload = dict()
        self.interest_over_time_widget = dict()

    def GetGoogleCookie(self):
        """
        Gets google cookie (used for each and every proxy; once on init otherwise)
        Removes proxy from the list on proxy error
        """
        while True:
            proxy = {'https': self.proxies[0]}
            try:
                return dict(filter(lambda i: i[0] == 'NID', requests.get(
                    'https://trends.google.com/?geo={geo}'.format(
                        geo=self.hl[-2:]),
                    timeout=self.timeout,
                    proxies=proxy,
                    **self.requests_args
                ).cookies.items()))
            except requests.exceptions.ProxyError:
                print(f'Proxy error. Changing IP {self.proxies[0]} self.kw_list {self.kw_list}')
                shuffle(self.proxies)
                continue

    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
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

        s.headers.update({'accept-language': self.hl, 'User-Agent': UserAgent().random})
        if len(self.proxies) > 0:
            self.cookies = self.GetGoogleCookie()
            s.proxies.update({'https': self.proxies[0]})
        if method == TrendReqV2.POST_METHOD:
            response = s.post(url, timeout=self.timeout,
                              cookies=self.cookies, **kwargs, **self.requests_args)  # DO NOT USE retries or backoff_factor here
        else:
            response = s.get(url, timeout=self.timeout, cookies=self.cookies,
                             **kwargs, **self.requests_args)   # DO NOT USE retries or backoff_factor here
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
            shuffle(self.proxies)
            return json.loads(content)
        else:
            # error
            raise exceptions.ResponseError(
                'The request failed: Google returned a '
                'response with code {0}.'.format(response.status_code),
                response=response)

    def build_payload(self, kw_list, cat=0, timeframe='today 5-y', geo='',
                      gprop=''):
        """Create the payload for related queries, interest over time and interest by region"""
        self.kw_list = kw_list
        self.geo = geo or self.geo
        self.token_payload = {
            'hl': self.hl,
            'tz': self.tz,
            'req': {'comparisonItem': [], 'category': cat, 'property': gprop}
        }

        # build out json for each keyword
        for kw in self.kw_list:
            keyword_payload = {'keyword': kw, 'time': timeframe,
                               'geo': self.geo}
            self.token_payload['req']['comparisonItem'].append(keyword_payload)
        # requests will mangle this if it is not a string
        self.token_payload['req'] = json.dumps(self.token_payload['req'])
        # get tokens
        self._tokens()
        results = self.interest_over_time()
        return results

    def _tokens(self):
        """Makes request to Google to get API tokens for interest over time, interest by region and related queries"""
        # make the request and parse the returned json
        widget_dict = self._get_data(
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
        req_json = self._get_data(
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
        for idx, kw in enumerate(self.kw_list):
            # there is currently a bug with assigning columns that may be
            # parsed as a date in pandas: use explicit insert column method
            result_df.insert(len(result_df.columns), kw,
                             result_df[idx].astype('int'))
            del result_df[idx]

        if 'isPartial' in df:
            # make other dataframe from isPartial key data
            # split list columns into seperate ones, remove brackets and split on comma
            df = df.fillna(False)
            result_df2 = df['isPartial'].apply(lambda x: pd.Series(
                str(x).replace('[', '').replace(']', '').split(',')))
            result_df2.columns = ['isPartial']
            # concatenate the two dataframes
            final = pd.concat([result_df, result_df2], axis=1)
        else:
            final = result_df
            final['isPartial'] = False

        return final

