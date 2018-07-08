"""Scrape property sales information from QV.co.nz."""
from requests_html import HTMLSession
from datetime import datetime
from settings import settings

SALES_SHEET = "Sales"
COLUMNS = ["Property", "Sale price", "Sale date"]
ID = "Property"


def convert_prices(price):
    """Convert price string to int"""
    return int(price.replace("Sale price: $", "").replace(",", ""))


def convert_date(date_str):
    return datetime.strptime(date_str.replace("Sold: ", ""), "%d/%m/%Y")


def get_sale_prices():
    """Scrape the most recent sales from the specified QV URL (region)."""
    session = HTMLSession()
    qv_hamilton = session.get(settings.qv_url)

    # Wait a bit and scroll down before scraping results to allow page to load
    qv_hamilton.html.render(wait=5, sleep=5, scrolldown=5, keep_page=True)

    sales_results = qv_hamilton.html.find("div#salesResults")[0]

    # Get property names
    properties = sales_results.find("a")
    addresses = [p.text for p in properties]

    # Get sale prices
    sale_prices = sales_results.find("h2")
    prices = [convert_prices(e.text) for e in sale_prices]

    dark_ps = sales_results.find("p.dark")  # class = dark
    dates = [convert_date(d.text) for d in dark_ps if d.text.startswith("Sold: ")]

    property_values = [
        {COLUMNS[0]: add, COLUMNS[1]: price, COLUMNS[2]: date}
        for add, price, date in zip(addresses, prices, dates)
    ]

    return property_values
