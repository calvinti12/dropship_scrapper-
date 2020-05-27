import statistics


class Site:
    def __init__(self, ranking, link, daily_visitors, monthly_visitors):
        self.ranking = ranking
        self.link = link
        self.daily_visitors = int(daily_visitors.replace(',', ''))
        self.monthly_visitors = int(monthly_visitors.replace(',', ''))
        self.stats = {}
        self.last90days_rank = 0
        self.today_rank = 0
        self.number_of_products = 0
        self.avg_product_price = 0
        self.median_product_price = 0
        self.strong_collection = '-'
        self.strong_type = '-'
        self.last_updated = '-'
        self.first_publish = '-'

    def add_stats(self, stats):
        self.stats = stats
        try:
            if len(stats) > 3:
                self.last90days_rank = stats[0]["rank"]
                self.today_rank = stats[3]["rank"]
            else:
                self.last90days_rank = stats[0]["rank"]
                self.today_rank = stats[2]["rank"]
        except Exception as e:
            print(f"Cant add_stats to site - {self.link} stats - {stats}", e)

    def set_products(self, number_of_products, avg_product_price, median_product_price, strong_collection, strong_type, last_updated, first_publish):
        self.number_of_products = number_of_products
        self.avg_product_price = avg_product_price
        self.median_product_price = median_product_price
        self.strong_collection = strong_collection
        self.strong_type = strong_type
        self.last_updated = last_updated
        self.first_publish = first_publish

    def set_products_lean(self, products):
        self.set_products(len(products['prices']), products['product_avg'] / len(products['prices']),
                          statistics.median(products['prices']), products['strong_collection'],
                          products['strong_type'], products['last_updated'], products['first_publish'])