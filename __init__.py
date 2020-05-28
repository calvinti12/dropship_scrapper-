from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from concurrent.futures import ThreadPoolExecutor

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()
sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())


def scrape_sites(sites):
    workers = int(len(sites) / 2)
    if workers == 0:
        workers = 1
    with ThreadPoolExecutor(max_workers=25) as executor:
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
    number_per_instance = 200
    while len(sites_to_update) > 0:
        worker_sites = []
        for x in range(number_per_instance):
            if len(sites_to_update) > 0:
                worker_sites.append(sites_to_update.pop(0))
        if len(worker_sites) > 0:
            scrape_sites(worker_sites)


if __name__ == "__main__":
    main()
