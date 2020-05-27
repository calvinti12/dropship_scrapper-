from Google.google_sheets import GoogleSheets
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from concurrent.futures import ThreadPoolExecutor
import random



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
    sites = []
    for row in range(row_number, row_number+number_per_instance):
        site = sites_sheet.get_site(row)
        if sites_sheet.should_update_site(site.link):
            sites.append(site)
        else:
            print(f"#{site.link} Was updated recently ")
    if len(sites) > 0:
        scrape_sites(sites, scrape_number)
        return True
    print("Finish all sites")
    return False


def scrape_sites(sites, scrape_number):
    with ThreadPoolExecutor(max_workers=int(len(sites)/2)) as executor:
        for site in sites:
            executor.submit(add_sites, site, scrape_number)


def add_sites(site, scrape_number):
    try:
        print(f"#{site.row_number} Working on - {site.link} using google function number {scrape_number}")
        site.add_stats(get_rank(site))
        products = get_store_products(site.link, scrape_number)
        if products:
            site.set_products_lean(products)
            sites_sheet.add_site_to_row_data(site)
        else:
            sites_sheet.add_error_site_to_row_data(sites_sheet.get_site(site.row_number))
    except Exception as e:
        print("Error in add_sites", e)


def main():
    _row_number = get_first_site_to_update(number_of_sites)
    _number_per_instance = 40
    _scrape_number = 1

    while get_sites(_row_number, _number_per_instance, _scrape_number):
        _row_number += _number_per_instance
        _scrape_number += 1
        if _scrape_number > 4:
            _scrape_number = 1


if __name__ == "__main__":
    main()
