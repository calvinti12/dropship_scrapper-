import json
import urllib.request

LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/shopify_scrapper_"


def get_store_products(link, scrape_number):

    req = urllib.request.Request(LINK+str(scrape_number) + '?link={}'.format(link))
    data = urllib.request.urlopen(req).read()
    products = json.loads(data.decode())
    return products


class GoogleFunction:
    pass
