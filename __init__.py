from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from Google.google_function import get_myips_link
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, json

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()


NUMBER_OF_WORKERS = 10
api = Flask(__name__)


@api.route('/update_all', methods=['GET'])
def update_all():
    update_all()
    return json.dumps("Started update_all")


@api.route('/update_zero_products', methods=['GET'])
def update_zero_products():
    update_zero_products()
    return json.dumps("Started update_zero_products")


@api.route('/ping', methods=['GET'])
def ping():
    return json.dumps("pong")


def scrape_sites(sites):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for site in sites:
            executor.submit(add_sites, site)


def scrape_my_ips(number_of_pages):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for page in range(1, number_of_pages):
            executor.submit(get_myips_link, page)


def add_sites(site):
    try:
        site.add_stats(get_rank(site))
        products = get_store_products(site.link)
        if products:
            site.set_products_lean(products)
            atlas.update_site(site)
            print(f"Finish {site.link}")
        else:
            atlas.update_site(site)
            print(f"Finish {site.link} with no products")

    except Exception as e:
        print(f"Error to  {site.link} with {e}")


def update_all():
    sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


def get_all_shops():
    scrape_my_ips(number_of_pages=1000)


def update_zero_products():
    sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


if __name__ == "__main__":
    get_all_shops()
    # api.run()

