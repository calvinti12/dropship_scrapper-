import json
import urllib.request
from Scrappers.shopify_scraper import analysis_site_test
from Scrappers.my_ips_ms_scrapper import analysis_page_test

STORE_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/store_scrapper_"
MYIPS_SCRAPPER_LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/myips_scrapper_"
DEBUG = False


def get_store_products(link):
    scrape_number = 1
    try:
        if DEBUG:
            products = json.loads(analysis_site_test(link))
            return products
        else:
            req = urllib.request.Request(STORE_SCRAPPER_LINK + str(scrape_number) + '?link={}'.format(link))
            data = urllib.request.urlopen(req).read()
            products = json.loads(data.decode())
            return products
    except Exception as e:
        print(f"Error in get_store_products link {link}", e)
    return


def get_myips_link(page):
    scrape_number = 1
    try:
        if DEBUG:
            ips = analysis_page_test(page)
            return ips
        else:
            req = urllib.request.Request(MYIPS_SCRAPPER_LINK + str(scrape_number) + '?page={}'.format(page))
            data = urllib.request.urlopen(req).read()
            ips = json.loads(data.decode())
            print(f"ips {ips}")
            return ips
    except Exception as e:
        print(f"Error in get_myips_link link {page}", e)
    return


class GoogleFunction:
    pass
