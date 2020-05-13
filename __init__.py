from google_sheets import GoogleSheets
# from Scrappers.my_ips_ms_scrapper import MyIpsMsScrapper
from Scrappers.awis_api_wrapper import get_rank
from Scrappers.niche_scrapper import NicheScrapper

# gts = GoogleTrends(["Acupressure Relief Mat"])


sites_sheet = GoogleSheets('Sites & products')
niche_scrapper = NicheScrapper("goffer14@gmail.com", "-7iMqAg6hp_wy*U")

number_of_sites = sites_sheet.get_last_row()-1

print(f"number_of_sites {number_of_sites}")

for row in range(0, number_of_sites):
    site = sites_sheet.get_site(row+2)
    print(f"#{row} Working on - " + site.link)
    site.add_stats(get_rank(site))
    product_stats = niche_scrapper.analysis_store(site)
    sites_sheet.add_site_to_row_data(site)

niche_scrapper.close_driver()


# results = gts.get_interest_over_time()
# print(results)
