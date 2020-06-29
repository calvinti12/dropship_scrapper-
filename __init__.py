import logging
import multiprocessing
import os
import random
import sys
import traceback
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from flask import Flask, request, jsonify , render_template

from Class.site import Site
from Database.atlas import MongoAtlas, evaluate_site, get_site_to_evaluate, add_site
from Frontpages.evaluate import open_site
from Google.google_function import get_ads_data_test, get_myips_link
from Google.google_function import get_facebook_data
from Google.google_function import get_store_products
from Google.google_function import scrape_my_ips
from Google.google_sheets import GoogleSheets
from Google.google_trends_api import get_interest_over_time
from Scrappers.Stats.awis_api_wrapper import get_rank

global main_thread

SCRAPE_WORKERS = int(os.getenv('SCRAPE_WORKERS', 50))
DEBUG = eval(os.getenv('DEBUG', 'False'))

sites_sheet = GoogleSheets('Sites & products')
atlas = MongoAtlas()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    logging.error("Unhandled exception: %s", text)


def start_scrape(function, items, processors):
    with ThreadPoolExecutor(max_workers=processors) as executor:
        for item in items:
            try:
                executor.submit(function, item)
            except Exception as e:
                print(f"Error to  {function.__name__} with {e} item {item}")


def load_data(link):
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        tasks = [executor.submit(get_rank, link),
                 executor.submit(get_store_products, link),
                 executor.submit(get_facebook_data, link)]

        futures.wait(tasks, timeout=70000, return_when=futures.ALL_COMPLETED)
        return tasks[0].result(), tasks[1].result(), tasks[2].result()


def update_facebook_data(site_link):
    try:
        facebook_ads = get_facebook_data(site_link)
        if 'ok' in facebook_ads['facebook'] and facebook_ads['facebook']['ok']:
            print(f"Finish update_facebook_data site {site_link}")
        else:
            print(f"Cant add ads to  {site_link}")
        atlas.add_facebook_ads(site_link, facebook_ads)
    except Exception as e:
        pass


def get_site_data(site):
    try:
        stats, products, facebook_ads = load_data(site.link)
        site.add_stats(stats)
        site.set_products_lean(products)
        site.add_ads(facebook_ads)

        atlas.update_site(site)
    except Exception as e:
        print(f"Error to  {site.link} with {e}")


def start_update(function, processors):
    sites_to_update = atlas.get_data(function, sites_sheet.get_sites())
    random.shuffle(sites_to_update)
    if len(sites_to_update):
        start_scrape(function, sites_to_update, processors)
    else:
        print(f"No more sites to {function}")


def test_facebook_data(site_link):
    facebook_data = get_facebook_data(site_link)
    if facebook_data:
        print(f"Finish {site_link} with facebook data")
    else:
        print(f"Finish {site_link} with no facebook data")


def test_facebook_ads(page_id):
    facebook_ads = get_ads_data_test(page_id)
    if facebook_ads:
        print(f"Finish {page_id} with facebook ads")
    else:
        print(f"Finish {page_id} with no facebook ads")


def test_site_data(link):
    site = sites_sheet.get_site_by_link(link)
    if site:
        get_site_data(site)


def print_loading_data():
    print("Number of cpu : ", multiprocessing.cpu_count())


@app.route("/evaluate", methods=['GET', 'POST'])
def evaluate():
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        if data:
            evaluate_site(data['data_link'][0],
                          eval(data['is_dropshipper'][0]),
                          data['main_product'][0],
                          eval(data['is_branded_products'][0]),
                          int(data['our_ranking'][0]))
    return open_site(get_site_to_evaluate())


@app.route("/start_update", methods=['GET', 'POST'])
def update_all():
    global main_thread
    function = request.args.get('update')
    processors = int(request.args.get('processors'))
    print('Received function API at process: ' + function)

    if not function:
        return "Missing data"

    data = {'processors': processors, 'function': get_site_data}
    if function == "facebook":
        data['function'] = update_facebook_data

    main_thread = Thread(target=start_update, kwargs=data)
    main_thread.start()

    # Immediately return a 200 response to the caller
    return "Started process"


@app.route("/start_msips_scrapper", methods=['GET'])
def start_msips_scrapper():
    global main_thread
    start_page = request.args.get('start_page')
    number_of_pages = int(request.args.get('number_of_pages'))
    attempts = int(request.args.get('attempts'))
    print('Received function API at process: start_msips_scrapper')

    data = {'start_page': start_page,
            'number_of_pages': number_of_pages,
            'attempts': attempts}

    main_thread = Thread(target=get_myips_link, kwargs=data)
    main_thread.start()

    # Immediately return a 200 response to the caller
    return "Started start_msips_scrapper process"


@app.route("/get_key_word_trend", methods=['GET'])
def get_key_word_trend():
    global main_thread
    data = request.form.to_dict(flat=False)
    main_thread = Thread(target=get_interest_over_time, kwargs={'kw_list': data})
    main_thread.start()
    return "try to print"


@app.route("/save_ips", methods=['POST'])
def save_ips():
    sites = request.json
    with ThreadPoolExecutor(max_workers=50) as executor:
        for site_data in sites:
            try:
                site = Site(ranking=site_data['ranking'],
                            link=site_data['link'],
                            daily_visitors=site_data['daily_visitors'],
                            monthly_visitors=site_data['monthly_visitors'])
                executor.submit(add_site, site)
            except Exception as e:
                print(f"Error to save_ips with {e} site_link {site_data['link']}")
    return "Saved save_ips"




if __name__ == '__main__':
    # app.run(debug=DEBUG)
    # sys.excepthook = log_except_hook
    # print_loading_data()
    get_interest_over_time(['wooden spoon'])
    # test_facebook_data('bodymattersgold.com')
    # test_site_data('bodymattersgold.com')


    # test_facebook_ads('323363524483195')
