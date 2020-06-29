import json
import os
import urllib.request
from Scrappers.Shops.shopify_scraper import analysis_site_test
from Scrappers.Ads.facebook_ad_library_scrapper import analysis_facebook_data_test
from Naked.toolshed.shell import execute_js, muterun_js


STORE_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/store_scrapper_"
MYIPS_SCRAPPER_LINK = "https://node-scrapper-ufmnftzakq-uk.a.run.app/scrape_ips"
FACEBOOK_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/facebook_scrapper_"
ADS_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/ads_scrapper_"
TIMEOUT = 60
DEBUG = eval(os.getenv('DEBUG', 'True'))


def get_store_products(link):
    scrape_number = 1
    try:
        if DEBUG:
            products = analysis_site_test(link)
            return products
        else:
            req = urllib.request.Request(STORE_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(link))
            data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
            products = json.loads(data.decode())
            return products
    except Exception as e:
        print(f"Error in get_store_products link {link}", e)


def get_myips_link(start_page, number_of_pages, attempts):
    try:
        req = urllib.request.Request(MYIPS_SCRAPPER_LINK + f'?start_page={start_page}&number_of_pages={number_of_pages}&attempts={attempts}')
        data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
        print(f"Start get_myips_link {start_page}", data)
    except Exception as e:
        print(f"Error in get_myips_link link {start_page}", e)


def get_facebook_data(site_link):
    scrape_number = 1
    try:
        if DEBUG:
            facebook_data = analysis_facebook_data_test(site_link)
            return facebook_data
        else:
            req = urllib.request.Request(FACEBOOK_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(site_link))
            data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
            facebook_data = json.loads(data.decode())
            return facebook_data
    except Exception as e:
        print(f"Error in get_facebook_ads link {site_link}", e)


def get_ads_data_test(page_id):
    scrape_number = 1
    try:
        if DEBUG:
            facebook_data = execute_js('./Scrappers/Ads/ads_scrapper.js')
            return facebook_data
        else:
            req = urllib.request.Request(
                ADS_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(page_id))
            data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
            ads = json.loads(data.decode())
        return ads
    except Exception as e:
        print(f"Error in get_ads_data link {page_id}", e)


def scrape_my_ips(number_of_pages):
    for page in range(2, number_of_pages):
        get_myips_link(page)


class GoogleFunction:
    pass
