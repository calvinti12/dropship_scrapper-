from google_sheets import GoogleSheets
from Scrappers.awis_api_wrapper import get_rank
from Scrappers.shopify_scraper import analysis_site
from Goggle.google_function import get_store_products
import time

# gts = GoogleTrends(["Acupressure Relief Mat"])

sites_sheet = GoogleSheets('Sites & products')
number_of_sites = sites_sheet.get_last_ips_site() - 1

print(f"number_of_sites {number_of_sites}")

for row in range(1, number_of_sites):
    start = time.time()
    site_link = ""
    try:
        site = sites_sheet.get_site(row+1)
        site_link = site.link
        if sites_sheet.should_update_site(site.link):
            print(f"#{row+1} Working on - " + site.link)
            site.add_stats(get_rank(site))
            products = get_store_products(site.link, 1)
            site.set_products_lean(products)

            # sites_sheet.add_site_to_row_data(site)
        else:
            print(f"#{site.link} Was updated recently ")
    except Exception as e:
        print(f"Error get_site row {row}", e)
        sites_sheet.add_error_site_to_row_data(sites_sheet.get_site(row+1))
    timer_site = '{:,.1f}'.format(float(time.time() - start))
    print(f'Time for {site_link} :{timer_site}s')

