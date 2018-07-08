"Module for grabbing existing properties and adding new properties"
# coding: utf-8

import openpyxl
from settings import settings

SHEET_NAME = "Properties"
ID = "id"
HEADERS_ROW = 1
COLUMNS_TO_KEEP = [
    "id",
    "Location",
    "Price",
    "Property type",
    "Rateable value (RV)",
    "Rooms",
    "href",
    "Floor area",
    "Land area",
    "Date listed",
]


def create_workbook_if_not_present():
    try:
        openpyxl.load_workbook(EXCEL_FILE)
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        sh = wb.active
        sh.title = SHEET_NAME
        sh.append(COLUMNS_TO_KEEP)
        wb.save(settings.excel_file_address)


def get_current_ids():
    xl_sheet = openpyxl.load_workbook(settings.excel_file_address)[SHEET_NAME]

    # Ascertain the ID column
    headers = xl_sheet[HEADERS_ROW]
    id_column = [cell.column for cell in headers if cell.value == ID][0]

    # Turn IDs into a set
    property_id_cells = xl_sheet[id_column]
    property_id_set = {cell.value for cell in property_id_cells[1:]}
    return property_id_set


def save_file(data):
    xl_wb = openpyxl.load_workbook(settings.excel_file_address)
    xl_sheet = xl_wb[SHEET_NAME]
    data_list = [[row.get(key, "") for key in COLUMNS_TO_KEEP] for row in data]

    for row in data_list:
        xl_sheet.append(row)

    xl_wb.save(settings.excel_file_address)


if __name__ == "__main__":
    print(get_current_ids())
