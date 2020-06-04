import re
from dateutil.parser import parse
from urllib.parse import urlencode
from requests_html import HTMLSession
import urllib.request
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from flask import jsonify
import datetime

FACEBOOK_ADS_LIBRARY = 'https://www.facebook.com/ads/library/?{}'
AD_CALZZ = '_7owt'
NUMBER_OF_LIKES = '_8wi7'
PAGE_CREATED = '_3-99'
ACTIVE_ADS = '_7gn2'
LATEST_RUNNING_AD = '_7jwu'
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
    'Connection': 'keep-alive',
    'User-Agent': '',
}


def class_to_css_selector(clazz):
    # This handles compound class names.
    return ".{}".format(clazz.replace(' ', '.'))


def scrapper(site_link, ads):
    try:
        qs = {
            'active_status': "all",
            'country': "ALL",
            'ad_type': "all",
            'impression_search_field': "has_impressions_lifetime",
            'view_all_page_id': ads['facebook']['page_id']
        }
        headers['User-Agent'] = UserAgent().random
        session = HTMLSession(browser_args=["--no-sandbox", "--user-agent=" + UserAgent().random])
        r = session.get(FACEBOOK_ADS_LIBRARY.format(urlencode(qs)), headers=headers)
        r.html.render(timeout=30)
        r.html.find(class_to_css_selector(ACTIVE_ADS), first=True)

        ads['facebook']['active_ads'] = int(re.findall(r'\d+', r.html.find(class_to_css_selector(ACTIVE_ADS), first=True).text.replace(',', ''))[0])
        likes_followers = r.html.find(class_to_css_selector(NUMBER_OF_LIKES))
        ads['facebook']['likes'] = int(likes_followers[0].text.split('\n')[0].replace(',', ''))
        ads['facebook']['niche'] = likes_followers[0].text.split('\n')[2]

        if len(likes_followers) > 1:
            ads['facebook']['instagram_followers'] = int(likes_followers[1].text.split(' ')[0].replace(',', ''))

        ads['facebook']['page_created'] = parse(r.html.find(class_to_css_selector(PAGE_CREATED))[2].text).date()
        new_ad_divs = r.html.find(class_to_css_selector(AD_CALZZ))
        for ad_div in new_ad_divs:
            updated = extract_date(ad_div.find(class_to_css_selector(LATEST_RUNNING_AD), first=True).text)
            if parse(ads['facebook']['latest_running_ad']).date() < updated:
                ads['facebook']['latest_running_ad'] = str(updated)
    except Exception as e:
        print(f"Error to getting facebook ads for site_link  {site_link} with {e}")
    return ads


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
        site_ads = scrapper(site_data[0], ads)
        return site_ads


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


def extract_date(date_str):
    return parse(date_str.lower().replace('started running on ', '')).date()


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

    if request_json and 'site_link' in request_json:
        site_link = request_json['site_link']
    elif request_args and 'site_link' in request_args:
        site_link = request_args['site_link']
    else:
        return "Not valid site_link"
    try:
        return jsonify(get_ads_by_page_id(site_link))
    except Exception as e:
        print(f"Error in analysis_facebook_ads {e}")


def analysis_facebook_ads_test(site_link):
    try:
        return get_ads_by_page_id(site_link)
    except Exception as e:
        print(f"Error in analysis_facebook_ads_test {e}")


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