import re
import json
import urllib.request
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from flask import jsonify
import datetime

ADS_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/ads_scrapper_"
TIMEOUT = 60
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
    'Connection': 'keep-alive',
    'User-Agent': '',
}


def get_ads_by_page_id(site_link):
    ads = init_ads()
    site_link = fix_url(site_link)
    site_data = extract_social_page_links(site_link)
    page_id = extract_facebook_page_id(site_data[0])

    ads['facebook']['page_id'] = page_id
    ads['facebook']['link'] = site_data[0]
    ads['twitter']['link'] = site_data[1]
    ads['instagram']['link'] = site_data[2]
    ads['youtube']['link'] = site_data[3]
    if page_id:
        facebook_ads = get_ads_data(page_id, site_link)
        ads['facebook'] = facebook_ads
        ads['facebook']['link'] = site_data[0]
    return ads


def extract_facebook_page_id(facebook_page_url):
    soup = get_soup(facebook_page_url)
    ios_page = soup.find("meta", property="al:ios:url")
    android_page = soup.find("meta", property="al:android:url")
    page_id = extract_page_id(ios_page, android_page)
    return page_id


def extract_social_page_links(site_link):
    soup = get_soup(site_link)
    raw_links = soup.findAll('a', attrs={'href': re.compile("^http://")}) + soup.findAll('a', attrs={'href': re.compile("^https://")})
    social_links = extract_social_links(raw_links, site_link)
    return social_links


def get_soup(link):
    headers['User-Agent'] = UserAgent().random
    req = urllib.request.Request(link, data=None, headers=headers)
    web_page = urllib.request.urlopen(req).read()
    return BeautifulSoup(web_page, "lxml")


def extract_page_id(ios_page, android_page):
    if ios_page:
        return re.findall(r'\d+', ios_page["content"])[0]
    if android_page:
        return re.findall(r'\d+', android_page["content"])[0]


def extract_social_links(links, site_link):
    if len(links) > 0:
        return [get_link(links, "facebook"), get_link(links, "twitter"), get_link(links, "instagram"), get_link(links, "youtube")]
    else:
        print(f'Cant get extract_social_links site_link {site_link}')


def get_link(hrefs, social_media):
    for link in hrefs:
        if social_media in link['href']:
            return link['href']
    return ''


def analysis_facebook_ads(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'link' in request_json:
        site_link = request_json['link']
    elif request_args and 'link' in request_args:
        site_link = request_args['link']
    else:
        return "Not valid site_link"
    try:
        return jsonify(get_ads_by_page_id(site_link))
    except Exception as e:
        print(f"Error in analysis_facebook_ads {e}")


def analysis_facebook_data_test(site_link):
    try:
        return get_ads_by_page_id(site_link)
    except Exception as e:
        print(f"Error in analysis_facebook_ads_test {e}")


def get_ads_data(page_id, site_link):
    scrape_number = 1
    try:
        req = urllib.request.Request(ADS_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(page_id))
        data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
        ads = json.loads(data.decode())
        return ads
    except Exception as e:
        print(f"Error in get_ads_data link {site_link}", e)


def init_ads():
    return {
            "facebook": {
                'link': '',
                'page_id': '',
                'active_ads': 0,
                'latest_running_ad': '01/01/1971',
                'likes': 0,
                'instagram_followers': 0,
                'niche': '',
                'page_created': datetime.datetime.now(datetime.timezone.utc),
                'updated': datetime.datetime.now(datetime.timezone.utc)
            },
            "twitter": {
                'link': '',
            },
            "instagram": {
                'link': '',
            },
            "youtube": {
                'link': '',
            },
            "google": {

            },
        }


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
            not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url
    return fixed_url.rstrip('/')
