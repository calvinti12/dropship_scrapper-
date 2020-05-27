from google_sheets import GoogleSheets
from Scrappers.awis_api_wrapper import get_rank
from Scrappers.shopify_scraper import analysis_site
from Goggle.google_function import get_store_products
import time
import asyncio
import tracemalloc

tracemalloc.start()

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
number_of_sites = sites_sheet.get_last_ips_site() - 1
print(f"number_of_sites {number_of_sites}")

def get_first_site_to_update(_number_of_sites):
    for row in range(1, _number_of_sites):
        if sites_sheet.should_update_site(sites_sheet.get_site(row).link):
            return row
    return _number_of_sites


def get_sites(row_number, number_per_instance, scrape_number):
    tasks = []
    loop = asyncio.new_event_loop()
    for row in range(row_number, row_number+number_per_instance):
        site = sites_sheet.get_site(row)
        if sites_sheet.should_update_site(site.link):
            tasks.append(loop.create_task(add_sites(site, scrape_number)))
        else:
            print(f"#{site.link} Was updated recently ")
    if len(tasks) > 0:
        asyncio.gather(tasks)
        return True
    print("Finish all sites")
    return False


async def add_sites(site, scrape_number):
    print(f"#{site.row_number} Working on - " + site.link)
    site.add_stats(await get_rank(site))
    products = await get_store_products(site.link, scrape_number)
    if products:
        site.set_products_lean(products)
        sites_sheet.add_site_to_row_data(site)
    else:
        sites_sheet.add_error_site_to_row_data(sites_sheet.get_site(site.row_number))


def main():
    _row_number = get_first_site_to_update(number_of_sites)
    _number_per_instance = 5
    _scrape_number = 1
    get_sites(_row_number, _number_per_instance, _scrape_number)


if __name__ == "__main__":
    main()
