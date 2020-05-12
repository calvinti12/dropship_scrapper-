from Scrappers.google_trends_api import GoogleTrends
from google_sheets import GoogleSheets
# from Scrappers.my_ips_ms_scrapper import MyIpsMsScrapper
from Scrappers.awis_api_wrapper import Awis_api

# gts = GoogleTrends(["Acupressure Relief Mat"])


sites_sheet = GoogleSheets('Sites & products')

number_of_sites = sites_sheet.get_last_row()-1

for row in range(0, number_of_sites):
    site = sites_sheet.get_site(row+2)
    myAwis_api = Awis_api(site)


# results = gts.get_interest_over_time()
# print(results)
