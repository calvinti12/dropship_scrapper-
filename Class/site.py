class Site:
    def __init__(self, name, link, daily_visitors, monthly_visitors):
        self.name = name
        self.link = link
        self.daily_visitors = daily_visitors
        self.monthly_visitors = monthly_visitors
        self.stats = {}
        self.last90days_rank = 0
        self.today_rank = 0
        self.number_of_products = 0
        self.avg_product_price = 0
        self.median_product_price = 0

    def add_stats(self, stats):
        self.stats = stats
        self.last90days_rank = stats[0]["rank"]
        self.today_rank = stats[3]["rank"]

    def set_products(self, number_of_products, avg_product_price, median_product_price):
        self.number_of_products = number_of_products
        self.avg_product_price = avg_product_price
        self.median_product_price = median_product_price
