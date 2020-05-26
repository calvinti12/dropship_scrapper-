class Site:
    def __init__(self, ranking, link, daily_visitors, monthly_visitors):
        self.ranking = ranking
        self.link = link
        self.daily_visitors = daily_visitors
        self.monthly_visitors = monthly_visitors
        self.stats = {}
        self.last90days_rank = 0
        self.today_rank = 0
        self.number_of_products = 0
        self.avg_product_price = 0
        self.median_product_price = 0
        self.strong_collection = ''
        self.last_updated = ''
        self.first_publish = ''

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
            print(f"Cant add_stats to site - {self.link}", e)

    def set_products(self, number_of_products, avg_product_price, median_product_price, strong_collection, last_updated, first_publish):
        self.number_of_products = number_of_products
        self.avg_product_price = avg_product_price
        self.median_product_price = median_product_price
        self.strong_collection = strong_collection
        self.last_updated = last_updated
        self.first_publish = first_publish

