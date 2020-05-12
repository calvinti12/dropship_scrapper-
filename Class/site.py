class Site:
    def __init__(self, name, link, daily_visitors, monthly_visitors):
        self.name = name
        self.link = link
        self.daily_visitors = daily_visitors
        self.monthly_visitors = monthly_visitors
        self.stats = {}

    def add_stats(self, stats):
        self.stats = stats
