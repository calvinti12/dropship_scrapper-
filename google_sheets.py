# https://gspread.readthedocs.io/en/latest/oauth2.html
import gspread
from datetime import date
from Class.site import Site
from google.oauth2.service_account import Credentials
global sites_worksheet
global row_data_worksheet
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


def find_product_cell_row(product):
    try:
        cell = sites_worksheet.find(product)
        print("Found item at R%sC%s" % (cell.row, cell.col))
        return cell.row
    except Exception as e:
        print("Cant find product", e)
        return next_available_row(sites_worksheet)


def find_site_cell_row(site):
    try:
        cell = sites_worksheet.find(site.link)
        print("Found item at R%sC%s" % (cell.row, cell.col))
        return cell.row
    except Exception as e:
        print("Cant find product", e)
        return next_available_row(row_data_worksheet)


def next_available_row(work_sheet):
    str_list = list(filter(None, work_sheet.col_values(1)))
    return str(len(str_list) + 1)


def get_cell_value(col, row):
    return sites_worksheet.acell(f"{str(col)}{str(row)}").value


class GoogleSheets:
    def __init__(self, sheet_name):
        global sites_worksheet
        global row_data_worksheet
        credentials = Credentials.from_service_account_file('sheets_key.json', scopes=scopes)
        gc = gspread.authorize(credentials)
        sites_worksheet = gc.open(sheet_name).worksheet("Myip_sites")
        row_data_worksheet = gc.open(sheet_name).worksheet("Raw_data")

    def add_product_to_sheet(self, product):
        row = find_product_cell_row(product)
        sites_worksheet.update_acell("A{}".format(row), product)
        # sheet.update_acell("B{}".format(row), product)

    def get_last_row(self):
        return int(next_available_row(sites_worksheet))-1

    def get_site(self, row_number):
        return Site(name=get_cell_value("B", row_number),
                    link=get_cell_value("C", row_number),
                    daily_visitors=get_cell_value("D", row_number),
                    monthly_visitors=get_cell_value("E", row_number))

    def add_site_to_row_data(self, site):
        row = find_site_cell_row(site)
        row_data_worksheet.update(f"C{row}", site.link)
        row_data_worksheet.update(f"D{row}", site.last90days_rank)
        row_data_worksheet.update(f"E{row}", site.today_rank)
        row_data_worksheet.update(f"F{row}", site.daily_visitors)
        row_data_worksheet.update(f"G{row}", site.monthly_visitors)
        row_data_worksheet.update(f"H{row}", site.avg_product_price)
        row_data_worksheet.update(f"I{row}", site.median_product_price)
        row_data_worksheet.update(f"K{row}", site.number_of_products)
        row_data_worksheet.update(f"L{row}", date.today().strftime("%d/%m/%Y"))




