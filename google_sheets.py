# https://gspread.readthedocs.io/en/latest/oauth2.html
import gspread
import datetime
from dateutil.parser import parse
from Class.site import Site
from google.oauth2.service_account import Credentials
global my_ips_sites_worksheet
global row_data_worksheet
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


def find_product_cell_row(product):
    try:
        cell = my_ips_sites_worksheet.find(product)
        return cell.row
    except Exception as e:
        print("Cant find product", e)
        return next_available_row(my_ips_sites_worksheet)


def find_site_cell_row(link):
    try:
        cell = my_ips_sites_worksheet.find(link)
        return cell.row
    except Exception as e:
        print("Cant find product", e)
        return next_available_row(row_data_worksheet)


def find_last_updated_site_date(link):
    try:
        cell = row_data_worksheet.find(link)
        return parse(row_data_worksheet.acell(f"L{str(cell.row)}").value)
    except Exception as e:
        print("Cant find product updated", e)
        return parse(str(datetime.date.today()))


def next_available_row(work_sheet):
    str_list = list(filter(None, work_sheet.col_values(1)))
    return str(len(str_list) + 1)


def get_cell_value(col, row):
    return my_ips_sites_worksheet.acell(f"{str(col)}{str(row)}").value


def add_data_to_row(row, data, link):
    try:
        row_data_worksheet.update(row, data)
    except Exception as e:
        print(f"Cant add data to row {row} to site {link}", e)


class GoogleSheets:
    def __init__(self, sheet_name):
        global my_ips_sites_worksheet
        global row_data_worksheet
        credentials = Credentials.from_service_account_file('sheets_key.json', scopes=scopes)
        gc = gspread.authorize(credentials)
        my_ips_sites_worksheet = gc.open(sheet_name).worksheet("Myip_sites")
        row_data_worksheet = gc.open(sheet_name).worksheet("Raw_data")

    def get_last_row(self):
        return int(next_available_row(my_ips_sites_worksheet)) - 1

    def get_site(self, row_number):
        return Site(ranking=get_cell_value("B", row_number),
                    link=get_cell_value("C", row_number),
                    daily_visitors=get_cell_value("D", row_number),
                    monthly_visitors=get_cell_value("E", row_number))

    def should_update_site(self, link):
        last_updated = find_last_updated_site_date(link)
        return last_updated + datetime.timedelta(weeks=1) <= parse(str(datetime.date.today()))

    def add_site_to_row_data(self, site):
        row = find_site_cell_row(site.link)
        add_data_to_row(f"B{row}", site.ranking, site.link)
        add_data_to_row(f"C{row}", site.link, site.link)
        add_data_to_row(f"D{row}", site.last90days_rank, site.link)
        add_data_to_row(f"E{row}", site.today_rank, site.link)
        add_data_to_row(f"F{row}", site.daily_visitors, site.link)
        add_data_to_row(f"G{row}", site.monthly_visitors, site.link)
        add_data_to_row(f"H{row}", site.avg_product_price, site.link)
        add_data_to_row(f"I{row}", site.median_product_price, site.link)
        add_data_to_row(f"K{row}", site.number_of_products, site.link)
        add_data_to_row(f"L{row}", datetime.date.today().strftime("%d/%m/%Y"), site.link)



