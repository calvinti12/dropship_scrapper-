import requests
from bs4 import BeautifulSoup
global soup


def get_rank(site):
    global soup
    response = requests.get(f"https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=UsageStats&Url={site.link}",
                            headers={"x-api-key": "0dnOHsO6en6z4TzwaQF0H3fTmpM92vIvaO6EgcwJ",
                            "Accept": "*/*",
                            "X-Amz-Date": "amzdate",
                            "Authorization": "authorization_header",
                            "x-amz-security-token": "session_token",
                            "content-type": "content_type"})
    soup = BeautifulSoup(response.text.encode('utf-8'), 'xml')
    site_stats = []
    for stats in soup.find_all('UsageStatistic'):
        stat = {
            "time_frame": '',
            "rank": stats.Rank.Value.get_text(),
            "rank_delta": stats.Rank.Delta.get_text(),
            "reach": stats.Reach.Rank.Value.get_text(),
            "reach_delta": stats.Reach.Rank.Delta.get_text(),
            "reach_per_million": stats.Reach.PerMillion.Value.get_text(),
            "reach_per_million_delta": stats.Reach.PerMillion.Delta.get_text(),
            "page_views_rank": stats.PageViews.Rank.Value.get_text(),
            "page_views_delta": stats.PageViews.Rank.Delta.get_text(),
            "page_views_per_million": stats.PageViews.PerMillion.Value.get_text(),
            "page_views_per_million_delta": stats.PageViews.PerMillion.Delta.get_text(),
            "page_views_per_user": stats.PageViews.PerUser.Value.get_text(),
            "page_views_per_user_delta": stats.PageViews.PerUser.Delta.get_text()
        }
        if stats.find('Months'):
            stat["time_frame"] = stats.TimeRange.Months.get_text()
        else:
            stat["time_frame"] = stats.TimeRange.Days.get_text()
        site_stats.append(stat)
    return site_stats


class Awis_api:
    pass
