import requests
from bs4 import BeautifulSoup
from xmlutils.xml2csv import xml2csv

class Awis_api:
    def __init__(self, site):
        response = requests.get(f"https://awis.api.alexa.com/api?Action=UrlInfo&ResponseGroup=UsageStats&Url={site.link}",
                                headers={"x-api-key": "0dnOHsO6en6z4TzwaQF0H3fTmpM92vIvaO6EgcwJ",
                                "Accept": "*/*",
                                "X-Amz-Date": "amzdate",
                                "Authorization": "authorization_header",
                                "x-amz-security-token": "session_token",
                                "content-type": "content_type"})
        soup = BeautifulSoup(response.text.encode('utf-8'), 'xml')
        print(soup.prettify())

# soup.Awis.Results.Result.Alexa.TrafficData.UsageStatistics.UsageStatistic.Rank.Value
#
# soup.find_all('UsageStatistic')
#
# {
#     'timeRange':
#
#
# }