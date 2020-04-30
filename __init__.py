from Scrappers.google_trends_api import GoogleTrends
from google_sheets import GoogleSheets

from Scrappers.dropship_rabbit_scrapper import DropShipRabbitScrapper

gts = GoogleTrends(["Acupressure Relief Mat"])

dsrScrapper = DropShipRabbitScrapper("Ben Goffer", "3d@qU8kGmem9@Ju", GoogleSheets('dropshiprabbit products'))
# results = gts.get_interest_over_time()
# print(results)
