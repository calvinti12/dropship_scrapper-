import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.parser import parse
global soup


def extract_int(string_number):
    try:
        return int(string_number.replace('%', ''))
    except:
        return string_number.replace('%', '')


def extract_float(string_number):
    try:
        return float(string_number.replace('%', ''))
    except:
        return string_number.replace('%', '')


def get_rank(link):
    global soup
    response = requests.get(f"https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=UsageStats&Url={link}",
                            headers={"x-api-key": "0dnOHsO6en6z4TzwaQF0H3fTmpM92vIvaO6EgcwJ",
                            "Accept": "*/*",
                            "X-Amz-Date": "amzdate",
                            "Authorization": "authorization_header",
                            "x-amz-security-token": "session_token",
                            "content-type": "content_type"})
    soup = BeautifulSoup(response.text.encode('utf-8'), 'xml')
    site_stats = []
    try:
        site_usage_statistic = soup.find_all('UsageStatistic')
        for stats in site_usage_statistic:
            site_stats.append(extract_stats(stats))
    except Exception as e:
        print("Cant extract UsageStatistic", e)

    return site_stats


def extract_stats(stats):
    try:
        stat = {
            "stats_date": '',
            "rank": extract_int(stats.Rank.Value.get_text()),
            "rank_delta": extract_int(stats.Rank.Delta.get_text()),
            "reach": extract_int(stats.Reach.Rank.Value.get_text()),
            "reach_delta": extract_int(stats.Reach.Rank.Delta.get_text()),
            "reach_per_million": extract_float(stats.Reach.PerMillion.Value.get_text()),
            "reach_per_million_delta": extract_float(stats.Reach.PerMillion.Delta.get_text()),
            "page_views_rank": extract_int(stats.PageViews.Rank.Value.get_text()),
            "page_views_delta": extract_int(stats.PageViews.Rank.Delta.get_text()),
            "page_views_per_million": extract_float(stats.PageViews.PerMillion.Value.get_text()),
            "page_views_per_million_delta": extract_float(stats.PageViews.PerMillion.Delta.get_text()),
            "page_views_per_user": extract_float(stats.PageViews.PerUser.Value.get_text()),
            "page_views_per_user_delta": extract_float(stats.PageViews.PerUser.Delta.get_text())
        }
        if stats.find('Months'):
            stat["stats_date"] = parse(str(datetime.date.today() - datetime.timedelta(days=int(stats.TimeRange.Months.get_text())*30)))
        else:
            stat["stats_date"] = parse(str(datetime.date.today() - datetime.timedelta(days=int(stats.TimeRange.Days.get_text()))))
        return stat
    except Exception as e:
        print("Cant extract_stats item", e)
        return []


class AwisApi:
    pass
