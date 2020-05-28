from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from concurrent.futures import ThreadPoolExecutor

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()
sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())

NUMBER_OF_WORKERS = 100


def scrape_sites(sites):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for site in sites:
            executor.submit(add_sites, site)


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


def main():
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


if __name__ == "__main__":
    main()
