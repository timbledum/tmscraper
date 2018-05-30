"Module for grabbing existing properties and adding new properties"
# coding: utf-8

import openpyxl

EXCEL_FILE = "Trademe Property List.xlsx"
SHEET_NAME = "Properties"
ID = "id"
HEADERS_ROW = 1


def get_current_ids():
    xl_sheet = openpyxl.load_workbook(EXCEL_FILE).active
    
    # Ascertain the ID column
    headers = xl_sheet[HEADERS_ROW]
    id_column = [cell.column for cell in headers if cell.value == ID][0]

    # Turn IDs into a set
    property_id_cells = xl_sheet[id_column]
    property_id_set = {cell.value for cell in property_id_cells[1:]}
    return property_id_set


def save_file(data):
    xl_sheet = openpyxl.load_workbook(EXCEL_FILE).active
    


if __name__ == "__main__":
    print(get_current_ids())