from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from concurrent.futures import ThreadPoolExecutor

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()
sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())

NUMBER_OF_INSTANCE = 200
NUMBER_OF_WORKERS = 50


def scrape_sites(sites):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for site in sites:
            executor.submit(add_sites, site)


def add_sites(site):
    try:
        print(f"Working on - {site.link}")
        site.add_stats(get_rank(site))
        products = get_store_products(site.link)
        if products:
            site.set_products_lean(products)
            atlas.update_site(site)
        else:
            atlas.update_site(site)
    except Exception as e:
        print("Error in add_sites", e)


def main():
    while len(sites_to_update) > 0:
        worker_sites = []
        for x in range(NUMBER_OF_INSTANCE):
            if len(sites_to_update) > 0:
                worker_sites.append(sites_to_update.pop(0))
        if len(worker_sites) > 0:
            scrape_sites(worker_sites)


if __name__ == "__main__":
    main()
