
import json
import time
from collections import Counter
import statistics
from dateutil.parser import parse
from fake_useragent import UserAgent
import urllib.request
from urllib.error import HTTPError

MAX_ITEM_TO_STORE = 100

proxy_host = 'localhost:1234'


def get_page(url, page, user_agent, collection_handle=None):
    full_url = url
    if collection_handle:
        full_url += '/collections/{}'.format(collection_handle)
    full_url += '/products.json'
    req = urllib.request.Request(
        full_url + '?page={}'.format(page),
        data=None,
        headers={
            'User-Agent': user_agent
        }
    )
    while True:
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            print('Blocked! Sleeping...')
            time.sleep(180)
            print('Retrying')

    products = json.loads(data.decode())['products']
    return products


def get_page_collections(url, user_agent):
    full_url = url + '/collections.json'
    page = 1
    while True:
        req = urllib.request.Request(
            full_url + '?page={}'.format(page),
            data=None,
            headers={
                'User-Agent': user_agent
            }
        )
        while True:
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                print('Blocked! Sleeping...')
                time.sleep(180)
                print('Retrying')

        cols = json.loads(data.decode())['collections']
        if not cols:
            break
        for col in cols:
            yield col
        page += 1


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
            not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url

    return fixed_url.rstrip('/')


def extract_products_collection(url, user_agent, col):
    page = 1
    products = get_page(url, page, user_agent, col)
    while products:
        for product in products:
            try:
                if product['variants'][0]:
                    product_id = product['id']
                    title = product['title']
                    product_type = product['product_type']
                    published_at = product['published_at']
                    updated_at = product['updated_at']
                    stock = str(product['variants'][0]['available'])
                    price = product['variants'][0]['price']
                    row = {'product_id': str(product_id),
                           'product_type': product_type,
                           'title': title,
                           'price': price,
                           'stock': stock,
                           'published_at': published_at,
                           'updated_at': updated_at,
                           'variants': str(len(product['variants']))}
                    for k in row:
                        row[k] = str(row[k].strip()) if row[k] else ''
                    yield row
                else:
                    yield
            except Exception as e:
                print(f"Error in extract_products_collection", e)
                yield
        page += 1
        products = get_page(url, page, user_agent, col)


def extract_products(url, user_agent):
    seen_products_id = set()
    products = {
        'product_avg': 0,
        'prices': [],
        'first_publish': '01/01/2090',
        'last_updated': '01/01/1971',
        'collection': [],
        'type': [],
        'strong_collection': '',
        'strong_type': ''
    }

    for col in get_page_collections(url, user_agent):
        for product in extract_products_collection(url, user_agent, col['handle']):
            try:
                if product and (product['product_id'] in seen_products_id or not bool(product['stock'])):
                    continue
                products['product_avg'] += float(product['price'])
                products['prices'].append(float(product['price']))
                products['collection'].append(col['handle'])
                products['type'].append(product['product_type'])
                if parse(products['first_publish']).date() > parse(product['published_at']).date():
                    products['first_publish'] = str(parse(product['published_at']).date())
                if parse(products['last_updated']).date() < parse(product['updated_at']).date():
                    products['last_updated'] = str(parse(product['updated_at']).date())
                seen_products_id.add(product['product_id'])
                if len(seen_products_id) >= MAX_ITEM_TO_STORE:
                    return products
            except Exception as e:
                print(f"Error in extract_products", e)
    return products


def analysis_site(site):
    products = extract_products(fix_url(site.link), UserAgent().random)
    best_col = Counter(products['collection'])
    best_type = Counter(products['type'])
    products['strong_collection'] = list(best_col.keys())[0] + f"({best_col[list(best_col.keys())[0]]})"
    products['strong_type'] = list(best_type.keys())[0] + f"({best_type[list(best_type.keys())[0]]})"
    site.set_products(len(products['prices']), products['product_avg'] / len(products['prices']), statistics.median(products['prices']), products['strong_collection'], products['strong_type'], products['last_updated'], products['first_publish'])


class ShopifyScrapper:
    pass
