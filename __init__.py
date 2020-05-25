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
    try:
        site = sites_sheet.get_site(row+2)
        if sites_sheet.should_update_site(site.link):
            print(f"#{row} Working on - " + site.link)
            site.add_stats(get_rank(site))
            niche_scrapper.analysis_store(site)
            sites_sheet.add_site_to_row_data(site)
        else:
            print(f"#{site.link} Was updated recently ")
    except Exception as e:
        print(f"Error get_site", e)

niche_scrapper.close_driver()


# results = gts.get_interest_over_time()
# print(results)
