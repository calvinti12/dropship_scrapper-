import statistics


def extract_number(string_number):
    return int("".join(filter(str.isdigit, string_number)))


class Site:
    def __init__(self, row_number, ranking, link, daily_visitors, monthly_visitors):
        self.row_number = row_number
        self.ranking = extract_number(ranking.replace(',', ''))
        self.link = link
        self.daily_visitors = int(daily_visitors.replace(',', ''))
        self.monthly_visitors = int(monthly_visitors.replace(',', ''))
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
        self.stats = stats

    def add_ads(self, ads):
        self.ads = ads

    def set_products(self, number_of_products, avg_product_price, median_product_price, strong_collection, strong_type, last_updated, first_publish, products):
        self.number_of_products = number_of_products
        self.avg_product_price = avg_product_price
        self.median_product_price = median_product_price
        self.strong_collection = strong_collection
        self.strong_type = strong_type
        self.last_updated = last_updated
        self.first_publish = first_publish
        self.products = products

    def set_products_lean(self, products):
        self.set_products(len(products['prices']), products['product_avg'] / len(products['prices']),
                          statistics.median(products['prices']), products['strong_collection'],
                          products['strong_type'], products['last_updated'], products['first_publish'], products['products'])
