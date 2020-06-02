import pymongo
import datetime
from dateutil.parser import parse

global sites
global sites_analysis
global ads

UPDATE_DATA_EVERY_DAYS = 1


def toDate(date_string):
    try:
        return parse(date_string)
    except Exception as e:
        return date_string


def get_link(site):
    return str(site['link'])


def add_site_analysis(site):
    for product in site.products:
        product['published_at'] = toDate(product['published_at'])
        product['updated_at'] = toDate(product['updated_at'])

    update_query = {
        "$set": {"link": site.link},
        "$push": {"stats": {
            "$each": [{
                "ranking": site.ranking,
                "daily_visitors": '{:,}'.format(int(site.daily_visitors)),
                "monthly_visitors": '{:,}'.format(int(site.monthly_visitors)),
                "avg_product_price": '{:,}'.format(int(site.avg_product_price)),
                "median_product_price": '{:,}'.format(int(site.median_product_price)),
                "number_of_product": site.number_of_products,
                "strong_collection": site.strong_collection,
                "strong_product": site.strong_type,
                "products": site.products,
                "updated": datetime.datetime.now(datetime.timezone.utc),
                "alexa": site.stats
            }],
            "$sort": {"updated": -1}
        }}
    }
    sites_analysis.update_one({'link': site.link}, update_query, upsert=True)


class MongoAtlas:
    def __init__(self):
        global sites
        global sites_analysis
        global ads
        client = pymongo.MongoClient(
            "mongodb+srv://Ben:30ulLucga43V4Slf@production.ohsz6.gcp.mongodb.net/test?retryWrites=true&w=majority")
        mydb = client.prodoction

        sites = mydb["sites"]
        sites_analysis = mydb["sites_analysis"]
        ads = mydb["ads"]

    def update_site(self, site):
        update_query = {"$set": {
            "ranking": site.ranking,
            "link": site.link,
            "number_of_product": site.number_of_products,
            "strong_collection": site.strong_collection,
            "strong_product": site.strong_type,
            "daily_visitors": '{:,}'.format(int(site.daily_visitors)),
            "last_product_updated": toDate(site.last_updated),
            "first_product_published": toDate(site.first_publish),
            "updated": datetime.datetime.now(datetime.timezone.utc)
        }}
        sites.update_one({'link': site.link}, update_query, upsert=True)
        add_site_analysis(site)

    def get_sites_to_update(self, sites_list):
        print(f"Total sites {len(sites_list)}")
        update_date = parse(str(datetime.date.today() - datetime.timedelta(days=UPDATE_DATA_EVERY_DAYS)))
        try:
            updated_sites = set(map(get_link, list(sites.find({"updated": {'$gte': update_date}}, {'_id': 0, 'link': 1}))))
            print(f"Total updated sites {len(updated_sites)}")
            sites_list[:] = [site for site in sites_list if not str(site.link) in updated_sites]
            print(f"Total sites to process {len(sites_list)}")
            return sites_list
        except Exception as e:
            print("Cant get_sites_to_update", e)
        return sites_list

    def evaluate_site(self, link, is_dropshipper, niche, main_product, is_branded_products, our_ranking):
        update_query = {"$set": {
            "is_dropshipper": is_dropshipper,
            "niche": niche,
            "main_product": main_product,
            "is_branded_products": is_branded_products,
            "our_ranking": our_ranking
        }}
        print(f"save site evaluate {link} is_dropshipper {is_dropshipper} niche {niche} is_branded_products {is_branded_products} our_ranking {our_ranking}")
        sites.update_one({'link': link}, update_query, upsert=False)

    def get_site_to_evaluate(self):

        update_date = parse(str(datetime.date.today() - datetime.timedelta(days=30)))

        try:
            site = sites.find_one({"is_dropshipper": {'$exists': False},
                                   "number_of_product": {'$gte': 1, '$lte': 10},
                                   "last_product_updated": {'$gte': update_date}
                                   },
                                  {'_id': 0, 'link': 1, 'number_of_product': 1, 'last_product_updated': 1, 'first_product_published': 1})
            return site
        except Exception as e:
            print("Cant get_site_to_evaluate", e)
