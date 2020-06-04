import json
import urllib.request
from Scrappers.Shops.shopify_scraper import analysis_site_test
from Scrappers.Shops.my_ips_ms_scrapper import analysis_page_test
from Scrappers.Ads.facebook_ad_library_scrapper import analysis_facebook_data_test
from concurrent.futures import ThreadPoolExecutor


STORE_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/store_scrapper_"
MYIPS_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/myips_scrapper_"
FACEBOOK_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/facebook_scrapper_"
ADS_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/ads_scrapper_"

DEBUG = False


def get_store_products(link):
    scrape_number = 1
    try:
        if DEBUG:
            products = analysis_site_test(link)
            return products
        else:
            req = urllib.request.Request(STORE_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(link))
            data = urllib.request.urlopen(req).read()
            products = json.loads(data.decode())
            return products
    except Exception as e:
        print(f"Error in get_store_products link {link}", e)


def get_myips_link(page):
    scrape_number = 1
    try:
        if DEBUG:
            ips = analysis_page_test(page)
            return ips
        else:
            req = urllib.request.Request(MYIPS_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(page))
            data = urllib.request.urlopen(req).read()
            ips = json.loads(data.decode())
            print(f"ips {ips}")
            return ips
    except Exception as e:
        print(f"Error in get_myips_link link {page}", e)


def get_facebook_data(site_link):
    scrape_number = 1
    try:
        if DEBUG:
            facebook_data = analysis_facebook_data_test(site_link)
            return facebook_data
        else:
            req = urllib.request.Request(FACEBOOK_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(site_link))
            data = urllib.request.urlopen(req).read()
            facebook_data = json.loads(data.decode())
            return facebook_data
    except Exception as e:
        print(f"Error in get_facebook_ads link {site_link}", e)


def get_ads_data_test(page_id):
    scrape_number = 1
    try:
        req = urllib.request.Request(
            ADS_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(page_id))
        data = urllib.request.urlopen(req).read()
        ads = json.loads(data.decode())
        return ads
    except Exception as e:
        print(f"Error in get_ads_data link {page_id}", e)


def scrape_my_ips(number_of_pages):
    with ThreadPoolExecutor(max_workers=1) as executor:
        for page in range(2, number_of_pages):
            executor.submit(get_myips_link, page)


class GoogleFunction:
    pass
