import statistics
from dateutil.parser import parse


def extract_number(string_number):
    return int("".join(filter(str.isdigit, string_number)))


def extract_int(string_number):
    try:
        return int(string_number)
    except:
        return string_number


def extract_float(string_number):
    try:
        return float(string_number)
    except:
        return string_number


def format_product(product):
    product['price'] = extract_float(product['price'])
    product['variants'] = extract_int(product['variants'])
    product['published_at'] = toDate(product['published_at'])
    product['updated_at'] = toDate(product['updated_at'])
    return product


def toDate(date_string):
    try:
        return parse(date_string).astimezone()
    except Exception as e:
        return date_string


class Site:
    def __init__(self, row_number, ranking, link, daily_visitors, monthly_visitors):
        self.row_number = row_number
        self.ranking = extract_number(str(ranking.replace(',', '')))
        self.link = link
        self.daily_visitors = int(str(daily_visitors).replace(',', ''))
        self.monthly_visitors = int(str(monthly_visitors).replace(',', ''))
        self.stats = {}
        self.ads = {
            "facebook": {},
            "twitter": {},
            "instagram": {},
            "youtube": {}
        }
        self.number_of_products = 0
        self.avg_product_price = 0
        self.median_product_price = 0
        self.strong_collection = '-'
        self.strong_type = '-'
        self.last_updated = '-'
        self.first_publish = '-'
        self.products = []

    def add_stats(self, stats):
        if stats:
            self.stats = stats
        else:
            print(f"Finish {self.link} with no stats")

    def add_ads(self, ads):
        if ads:
            self.ads = ads
            ads['facebook'] = {
                'active_ads': int(ads['facebook']['active_ads']),
                'instagram_followers': int(str(ads['facebook']['instagram_followers']).replace(',', '')),
                'likes': int(str(ads['facebook']['likes']).replace(',', '')),
                'latest_running_ad': toDate(ads['facebook']['latest_running_ad']),
                'link': ads['facebook']['link'],
                'niche': ads['facebook']['niche'],
                'page_id': ads['facebook']['page_id'],
                'page_created': toDate(ads['facebook']['page_created']),
                'updated': toDate(ads['facebook']['updated']),
            }
        else:
            print(f"Finish {self.link} with no facebook ads")

    def set_products(self, number_of_products, avg_product_price, median_product_price, strong_collection, strong_type, last_updated, first_publish, products):
        self.number_of_products = number_of_products
        self.avg_product_price = float("{:.2f}".format(avg_product_price))
        self.median_product_price = median_product_price
        self.strong_collection = strong_collection
        self.strong_type = strong_type
        self.last_updated = last_updated
        self.first_publish = first_publish
        if len(products) > 0:
            self.products = list(map(format_product, products))

    def set_products_lean(self, products):
        if products:
            self.set_products(len(products['prices']), products['product_avg'] / len(products['prices']),
                              statistics.median(products['prices']), products['strong_collection'],
                              products['strong_type'], products['last_updated'], products['first_publish'],
                              products['products'])
        else:
            print(f"Finish {self.link} with no products")






