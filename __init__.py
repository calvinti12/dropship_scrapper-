from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Scrappers.awis_api_wrapper import get_rank
from Scrappers.site_evaluation import SiteEvaluation
from Google.google_function import get_store_products
from Google.google_function import get_myips_link
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()


NUMBER_OF_WORKERS = 1
app = Flask(__name__)

niche_list = ["Test1", "Test2", "Test3", "Test4", "Test5", "Test6"]


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
            not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url
    return fixed_url.rstrip('/')


@app.route("/")
def template_test():
    link = fix_url("ninnsports.com")
    site_evaluation = SiteEvaluation()
    site_evaluation.get_site(link)
    #
    # return render_template('template.html',
    #                        link=link,
    #                        number_of_products="number_of_products!",
    #                        last_product_updated="last_product_updated!",
    #                        niche_list=niche_list)


def scrape_sites(sites):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for site in sites:
            executor.submit(add_sites, site)


def scrape_my_ips(number_of_pages):
    with ThreadPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
        for page in range(2, number_of_pages):
            executor.submit(get_myips_link, page)


def add_sites(site):
    try:
        site.add_stats(get_rank(site))
        products = get_store_products(site.link)
        if products:
            site.set_products_lean(products)
            atlas.update_site(site)
            print(f"Finish {site.link}")
        else:
            atlas.update_site(site)
            print(f"Finish {site.link} with no products")

    except Exception as e:
        print(f"Error to  {site.link} with {e}")


def update_all():
    sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


def get_all_shops():
    scrape_my_ips(number_of_pages=3)


def update_zero_products():
    sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


if __name__ == '__main__':
    # app.run(debug=True)
    link = fix_url("ninnsports.com")
    site_evaluation = SiteEvaluation()
    site_evaluation.get_site(link)
