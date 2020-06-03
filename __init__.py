from Google.google_sheets import GoogleSheets
from Database.atlas import MongoAtlas
from Frontpages.evaluate import open_site
from Scrappers.awis_api_wrapper import get_rank
from Google.google_function import get_store_products
from Google.google_function import scrape_my_ips
from Google.google_function import get_facebook_ads
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

# gts = GoogleTrends(["Acupressure Relief Mat"])
sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/evaluate", methods=['GET', 'POST'])
def evaluate():
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        if data:
            atlas.evaluate_site(data['data_link'][0],
                                eval(data['is_dropshipper'][0]),
                                data['niche'][0],
                                data['main_product'][0],
                                eval(data['is_branded_products'][0]),
                                int(data['our_ranking'][0]))
    return open_site(atlas.get_site_to_evaluate())


@app.route("/Start_update")
def update_all():
    start_update_all()


def scrape_sites(sites):
    with ThreadPoolExecutor(max_workers=1) as executor:
        for site in sites:
            executor.submit(add_sites, site)


def add_sites(site):
    try:
        site.add_stats(get_rank(site.link))
        products = get_store_products(site.link)
        facebook_ads = get_facebook_ads(site.link)
        if products:
            site.set_products_lean(products)
            print(f"Finish add products to {site.link}")
        else:
            print(f"Finish {site.link} with no products")
        if facebook_ads:
            site.add_facebook_ads(facebook_ads)
            print(f"Finish add facebook ads to {site.link}")
        else:
            print(f"Finish {site.link} with facebook ads")
        atlas.update_site(site)
    except Exception as e:
        print(f"Error to  {site.link} with {e}")


def start_update_all():
    sites_to_update = atlas.get_sites_to_update(sites_sheet.get_sites())
    while len(sites_to_update) > 0:
        scrape_sites(sites_to_update)
    print(f"Finish all sites")


def get_all_shops():
    scrape_my_ips(number_of_pages=3)


if __name__ == '__main__':
    start_update_all()
    # add_sites("")
    # app.run(debug=True)
