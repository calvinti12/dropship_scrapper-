# https://gspread.readthedocs.io/en/latest/oauth2.html
import asyncio
import gspread
import datetime
from dateutil.parser import parse
from Class.site import Site
from google.oauth2.service_account import Credentials
global my_ips_sites_list
global sites

scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

UPDATED_COL = 15
SITE_CONVERSION = 0.02
UPDATE_DATA_EVERY_DAYS = 7


def get_value(col, row):
    return my_ips_sites_list[row][col]


def get_site(row_number):
    return Site(row_number=row_number, ranking=get_value(1, row_number),
                link=get_value(2, row_number),
                daily_visitors=get_value(3, row_number),
                monthly_visitors=get_value(4, row_number))


def get_last_ips_site():
    return int(len(my_ips_sites_list))


def load_all_sites():
    for row in range(1, get_last_ips_site()):
        sites.append(get_site(row))


class GoogleSheets:
    def __init__(self, sheet_name):
        global my_ips_sites_list
        global sites
        sites = []
        credentials = Credentials.from_service_account_file('Google/sheets_key.json', scopes=scopes)
        gc = gspread.authorize(credentials)
        my_ips_sites_list = gc.open(sheet_name).worksheet("Myip_sites").get_all_values()
        load_all_sites()

    def get_sites(self):
        return sites

