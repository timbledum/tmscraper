"""Scrape property sales information from QV.co.nz."""
import requests
from datetime import datetime
from settings import settings

SALES_SHEET = "Sales"
COLUMNS = ["Property", "Sale price", "Sale date", "Rates value"]
ID = "Property"

REQUEST_DATA = {
    "MIME Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "op": "qv_widgets.rspRecentlySold.rspRecentlySold",
    "subop": "lazyLoadData",
    "maxSearch": "30",
    "propertyDetailsNavpoint": "phoenix-656",
    "areaType": "ta",
}


def convert_prices(price):
    """Convert price string to int."""
    return int(price.replace("$", "").replace(",", ""))


def convert_date(date_str):
    """Convert date string to datetime."""
    return datetime.strptime(date_str, "%d/%m/%Y")


def process_property(prop):
    """Extract key information from supplied dicts."""
    output = {}
    output['Property'] = prop['PropertyAddress']
    output['Sale date'] = convert_date(prop['DateSold'])
    output['Sale price'] = convert_prices(prop['SalePrice'])
    output['Rates value'] = convert_prices(prop['CapitalValue'])
    return output
        
def get_sale_prices():
    """Scrape the most recent sales from the specified QV URL (region)."""

    r = requests.post(settings.qv_url, data=REQUEST_DATA)
    response = r.json()

    data_processed = [process_property(prop) for prop in response['LocalAreaSales']]

    return data_processed
