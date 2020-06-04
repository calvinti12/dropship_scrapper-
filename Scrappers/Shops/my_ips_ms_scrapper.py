import requests
import time
from flask import jsonify
from lxml import html
from fake_useragent import UserAgent


payload = {'getpage': 'yes',
           'lang': 'en'}


headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
    'Connection': 'keep-alive',
    'Content-Length': '19',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 's2_csrf_cookie_name=3c111c8c0e52355f4fad0f2723d1ed3d; PHPSESSID=k215kcd51cbpruhkkp66krqie6; sw=134.9; sh=66.3; _ga=GA1.2.797439241.1588021291; _gid=GA1.2.215352006.1588021291; __gads=ID=6030cdad3da56a15:T=1588021296:S=ALNI_MYHF2Zdj8vwDzyDcBxeBrzT6uLFMQ; s2_csrf_cookie_name=3c111c8c0e52355f4fad0f2723d1ed3d; _gat=1; s2_uGoo=36a7f2682b286c7f0722046b21c811cc5d795460; __unam=737437c-171bd71e950-2dd2390f-26',
    'Host': 'myip.ms',
    'Origin': 'https://myip.ms',
    'Referer': 'https://myip.ms/browse/sites/1/own/376714/sort/6/asc/1#sites_tbl_top',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def scraper(page):
    websites = []
    rankings = []

    time.sleep(5)
    url = f"https://myip.ms/ajax_table/sites/{page}/own/376714/sort/6"

    headers['User-Agent'] = UserAgent().random

    response = requests.request("POST", url, headers=headers, data=payload, files=[])

    page_resp = html.fromstring(response.text.encode('utf8'))

    # rankings
    for r in page_resp.xpath("//span[contains(text(), '#')]"):
        rankings.append(r.xpath('.//text()')[0].replace('#', '').replace(',', '').strip())

    # websites
    for w in page_resp.xpath("//*[@ri]"):
        websites.append(w.xpath(".//text()")[0])

    print(rankings, websites)

    return jsonify({'websites': len(websites), 'rankings': len(rankings)})


def analysis_page(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'link' in request_json:
        page = request_json['link']
    elif request_args and 'link' in request_args:
        page = request_args['link']
    else:
        return "Not valid page"

    return scraper(page)


def analysis_page_test(page):
    return scraper(page)
