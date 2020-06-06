import os
import json
import time
from collections import Counter
from dateutil.parser import parse
from fake_useragent import UserAgent
import urllib.request
from urllib.error import HTTPError
from flask import jsonify

MAX_ITEM_TO_STORE = int(os.getenv('MAX_ITEM_TO_STORE', 1000))


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
    number_retries = 3
    while True:
        if number_retries == 0:
            print(f'Stop after {number_retries} retries {full_url}')
            break
        try:
            data = urllib.request.urlopen(req).read()
            break
        except HTTPError:
            number_retries -= 1
            time.sleep(5)

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
        number_retries = 3
        while True:
            if number_retries == 0:
                print(f'Stop after {number_retries} retries {full_url}')
                break
            try:
                data = urllib.request.urlopen(req).read()
                break
            except HTTPError:
                number_retries -= 1
                time.sleep(5)

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
                    sku = product['variants'][0]['sku']
                    main_image_src = ''
                    if product['images']:
                        main_image_src = product['images'][0]['src']

                    row = {'product_id': str(product_id),
                           'sku': str(sku),
                           'main_image_src': str(main_image_src),
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
        'products': [],
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
                products['products'].append(product)
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


def analysis_site(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'link' in request_json:
        link = request_json['link']
    elif request_args and 'link' in request_args:
        link = request_args['link']
    else:
        return "Not valid link"

    try:
        products = extract_products(fix_url(link), UserAgent().random)
        best_col = Counter(products['collection'])
        best_type = Counter(products['type'])
        products['strong_collection'] = list(best_col.keys())[0] + f"({best_col[list(best_col.keys())[0]]})"
        products['strong_type'] = list(best_type.keys())[0] + f"({best_type[list(best_type.keys())[0]]})"
    except Exception as e:
        return f"Error in analysis_site {e}"

    return jsonify(products)


def analysis_site_test(link):
    try:
        products = extract_products(fix_url(link), UserAgent().random)
        best_col = Counter(products['collection'])
        best_type = Counter(products['type'])
        products['strong_collection'] = list(best_col.keys())[0] + f"({best_col[list(best_col.keys())[0]]})"
        products['strong_type'] = list(best_type.keys())[0] + f"({best_type[list(best_type.keys())[0]]})"
    except Exception as e:
        return f"Error in analysis_site {e}"

    return products


