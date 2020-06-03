import re
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from dateutil.parser import parse
from urllib.parse import urlencode
import urllib.request
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from flask import jsonify
import datetime

AD_CALZZ = '_7owt'
NUMBER_OF_LIKES = '_8wi7'
PAGE_CREATED = '_3-99'
ACTIVE_ADS = '_7gn2'
LATEST_RUNNING_AD = '_7jwu'


def class_to_css_selector(clazz):
    # This handles compound class names.
    return ".{}".format(clazz.replace(' ', '.'))


def scrapper(site_link, ads, headless=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')

    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    driver.implicitly_wait(10)
    try:
        qs = {
            'active_status': "all",
            'country': "ALL",
            'ad_type': "all",
            'impression_search_field': "has_impressions_lifetime",
            'view_all_page_id': ads['facebook']['page_id']
        }
        driver.get(
            'https://www.facebook.com/ads/library/?{}'.format(urlencode(qs)))
        sleep(5)
        try:
            driver.find_element_by_xpath('//div[contains(text(),"There are no ads matching")]')
            print('No results')
            return
        except NoSuchElementException:
            pass

        # Find the ad class
        print(f"Finding ad class for page_id {ads['facebook']['page_id']}")

        new_ad_divs = driver.find_elements_by_css_selector(class_to_css_selector(AD_CALZZ))
        likes_followers = driver.find_elements_by_css_selector(class_to_css_selector(NUMBER_OF_LIKES))
        ads['facebook']['likes'] = int(likes_followers[0].text.split('\n')[0].replace(',', ''))
        ads['facebook']['niche'] = likes_followers[0].text.split('\n')[2]
        if len(likes_followers) > 1:
            ads['facebook']['instagram_followers'] = int(likes_followers[1].text.split(' ')[0].replace(',', ''))
        ads['facebook']['page_created'] = parse(driver.find_elements_by_css_selector(class_to_css_selector(PAGE_CREATED))[2].text).date()
        ads['facebook']['active_ads'] = re.findall(r'\d+', driver.find_element_by_css_selector(class_to_css_selector(ACTIVE_ADS)).text.replace(',', ''))[0]
        for ad_div in new_ad_divs:
            updated = extract_date(ad_div.find_element_by_css_selector(class_to_css_selector(LATEST_RUNNING_AD)).text)
            if parse(ads['facebook']['latest_running_ad']).date() < updated:
                ads['facebook']['latest_running_ad'] = str(updated)
    except Exception as e:
        print(f"Error to getting facebook ads for site_link  {site_link} with {e}")
    finally:
        driver.close()
        driver.quit()
    print(f'Done get ads for site_link {site_link}')
    return ads


def get_ads_by_page_id(site_link, headless):
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
        site_ads = scrapper(site_link, ads, headless=headless)
        return site_ads


def extract_facebook_page_id(facebook_page_url):
    req = urllib.request.Request(facebook_page_url, data=None, headers={
            'User-Agent': UserAgent().random
        })
    web_page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(web_page, "lxml")
    ios_page = soup.find("meta", property="al:ios:url")
    android_page = soup.find("meta", property="al:android:url")
    page_id = extract_page_id(ios_page, android_page)
    return page_id


def extract_social_page_links(site_link):
    req = urllib.request.Request(site_link, data=None, headers={
            'User-Agent': UserAgent().random
        })
    web_page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(web_page, "lxml")
    social_links = extract_social_links(soup.findAll('a', attrs={'href': re.compile("^http://")}), site_link)
    return social_links


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
        return jsonify(get_ads_by_page_id(site_link, False))
    except Exception as e:
        return f"Error in analysis_facebook_ads {e}"


def analysis_facebook_ads_test(site_link):
    try:
        return get_ads_by_page_id(site_link, True)
    except Exception as e:
        return f"Error in analysis_facebook_ads {e}"


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