# https://gspread.readthedocs.io/en/latest/oauth2.html
import gspread
from google.oauth2.service_account import Credentials
global sheet

scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


def find_product_cell_row(product):
    try:
        cell = sheet.find(product)
        print("Found item at R%sC%s" % (cell.row, cell.col))
        return cell.row
    except Exception as e:
        print("Cant find product", e)
        return next_available_row()


def next_available_row():
    str_list = list(filter(None, sheet.col_values(1)))
    return str(len(str_list) + 1)


class GoogleSheets:
    def __init__(self, sheet_name):
        global sheet
        credentials = Credentials.from_service_account_file('sheets_key.json', scopes=scopes)

        gc = gspread.authorize(credentials)

        sheet = gc.open(sheet_name).sheet1

        print(sheet.get('A1'))

    def get_sheet(self):
        return sheet

    def add_product_to_sheet(self, product):
        row = find_product_cell_row(product)
        sheet.update_acell("A{}".format(row), product)
        # sheet.update_acell("B{}".format(row), product)


