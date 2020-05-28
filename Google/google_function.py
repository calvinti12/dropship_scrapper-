import json
import urllib.request
from Scrappers.shopify_scraper import analysis_site_test

LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/store_scrapper_"
DEBUG = False


def get_store_products(link, scrape_number):
    try:
        if DEBUG:
            products = json.loads(analysis_site_test(link))
            return products
        else:
            req = urllib.request.Request(LINK+str(scrape_number) + '?link={}'.format(link))
            data = urllib.request.urlopen(req).read()
            products = json.loads(data.decode())
            return products
    except Exception as e:
        print(f"Error in get_store_products link {link} scrape_number {scrape_number}", e)
    return


class GoogleFunction:
    pass
