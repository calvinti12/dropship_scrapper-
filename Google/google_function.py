import json
import urllib.request

LINK = "https://us-central1-dropshipscrapper.cloudfunctions.net/shopify_scrapper_"


def get_store_products(link, scrape_number):
    try:
        req = urllib.request.Request(LINK+str(scrape_number) + '?link={}'.format(link))
        data = urllib.request.urlopen(req).read()
        products = json.loads(data.decode())
        return products
    except Exception as e:
        print(f"Error in get_store_products link {link} scrape_number {scrape_number}", e)
    return


class GoogleFunction:
    pass
