# https://gspread.readthedocs.io/en/latest/oauth2.html
import gspread
import datetime
from dateutil.parser import parse
from Class.site import Site
from google.oauth2.service_account import Credentials
global my_ips_sites_list
global row_data_list
global row_data_worksheet
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

UPDATED_COL = 15
SITE_CONVERSION = 0.02
UPDATE_DATA_EVERY_DAYS = 7


def find_site_cell_row(link):
    try:
        for sublist in row_data_list:
            if sublist[2] == link:
                return parse(sublist[0])
    except Exception as e:
        print("Cant find product", e)
    return next_available_row()


def find_last_updated_site_date(link):
    try:
        for sublist in row_data_list:
            if sublist[2] == link:
                return parse(sublist[UPDATED_COL])

    except Exception as e:
        print("Cant find product updated", e)
        return parse(str(datetime.date.today() + datetime.timedelta(weeks=-2)))
    return parse(str(datetime.date.today() + datetime.timedelta(weeks=-2)))


def next_available_row():
    return str(len(row_data_list) + 1)


def get_value(col, row):
    return my_ips_sites_list[row][col]


class GoogleSheets:
    def __init__(self, sheet_name):
        global my_ips_sites_list
        global row_data_list
        global row_data_worksheet

        credentials = Credentials.from_service_account_file('sheets_key.json', scopes=scopes)
        gc = gspread.authorize(credentials)
        my_ips_sites_list = gc.open(sheet_name).worksheet("Myip_sites").get_all_values()
        row_data_worksheet = gc.open(sheet_name).worksheet("Raw_data")
        row_data_list = row_data_worksheet.get_all_values()

    def get_last_row(self):
        return int(len(my_ips_sites_list))

    def get_site(self, row_number):
        return Site(ranking=get_value(1, row_number),
                    link=get_value(2, row_number),
                    daily_visitors=get_value(3, row_number),
                    monthly_visitors=get_value(4, row_number))

    def should_update_site(self, link):
        last_updated = find_last_updated_site_date(link)
        return last_updated + datetime.timedelta(days=UPDATE_DATA_EVERY_DAYS) <= parse(str(datetime.date.today()))

    def add_site_to_row_data(self, site):
        row = find_site_cell_row(site.link)
        site_list = [str(int(row) - 1),
                     site.ranking,
                     site.link,
                     '{:,}'.format(int(site.last90days_rank)),
                     '{:,}'.format(int(site.today_rank)),
                     '{:,}'.format(int(site.daily_visitors)),
                     '{:,}'.format(int(site.monthly_visitors)),
                     '${:,.1f}'.format(float(site.avg_product_price)),
                     '${:,.1f}'.format(float(site.median_product_price)),
                     '${:,.0f}'.format((int(site.daily_visitors)*SITE_CONVERSION)*float(site.median_product_price)),
                     site.number_of_products,
                     site.strong_collection,
                     site.strong_type,
                     parse(site.last_updated).strftime("%d/%m/%Y"),
                     parse(site.first_publish).strftime("%d/%m/%Y"),
                     datetime.date.today().strftime("%d/%m/%Y")]
        row_data_list.append(site_list)
        row_data_worksheet.update(f'A{row}:P{row}', [site_list])

    def add_error_site_to_row_data(self, site):
        row = find_site_cell_row(site.link)
        site_list = [str(int(row) - 1),
                     site.ranking,
                     site.link,
                     '{:,}'.format(int(site.last90days_rank)),
                     '{:,}'.format(int(site.today_rank)),
                     '{:,}'.format(int(site.daily_visitors)),
                     '{:,}'.format(int(site.monthly_visitors)),
                     '${:,.1f}'.format(float(site.avg_product_price)),
                     '${:,.1f}'.format(float(site.median_product_price)),
                     '${:,.0f}'.format((int(site.daily_visitors)*SITE_CONVERSION)*float(site.median_product_price)),
                     site.number_of_products,
                     site.strong_collection,
                     site.strong_type,
                     site.last_updated,
                     site.first_publish,
                     datetime.date.today().strftime("%d/%m/%Y")]
        row_data_list.append(site_list)
        row_data_worksheet.update(f'A{row}:P{row}', [site_list])
