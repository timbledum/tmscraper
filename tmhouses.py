"""Extract data from trademe."""
import grequests
import requests
from bs4 import BeautifulSoup

from settings import settings

TM_SITE = r"https://www.trademe.co.nz"
FIND_LINKS = {"class": "tmp-search-card-list-view__link"}


def get_property_table(prop_response):
    """Find the table with the key property facts on a property page and return as dict."""
    prop_soup = BeautifulSoup(prop_response.text, "html.parser")

    listing_table = prop_soup.find(id="ListingAttributes")
    listing_table_rows = [row for row in listing_table.contents if row != "\n"]

    listing_dict = {}
    for p in listing_table_rows:
        key = p.contents[1].text.strip().replace(":", "")
        value = p.contents[3].text.strip().replace("\xad", "")
        listing_dict[key] = value

    listing_date = prop_soup.find(id="PriceSummaryDetails_ListedStatusText")
    listing_dict["Date listed"] = listing_date.text[8:18].replace(",", "") + " 18"

    return listing_dict


def get_href_id(prop):
    """Helper function to extract key property information from trademe search site (url and ID)."""
    output = {}
    output["href"] = prop["href"]
    output["id"] = prop["id"]
    return output


def get_properties(page):
    """Get the property urls from the trademe search screen and populate with underlying information."""
    page_request = requests.get(page)
    page_html = page_request.text
    page_bs = BeautifulSoup(page_html, "html.parser")
    properties = page_bs.find_all(**FIND_LINKS)
    data = [get_href_id(prop) for prop in properties]
    return data

def get_page_urls(tm_url):
    """Get list of pages from trademe."""
    tm_request = requests.get(tm_url)
    html = tm_request.text
    html_bs = BeautifulSoup(html, "html.parser")
    next_links = html_bs.find(id="PagingFooter")("a")[:-1]
    return [tm_url] + [TM_SITE + a["href"] for a in next_links]


def get_property_pages(properties):
    """Concurrently process the property urls provided."""

    urls = [prop['href'] for prop in properties]
    requests = [grequests.get(TM_SITE + url) for url in urls]
    responses = grequests.map(requests, size=5)
    return responses


def get_trademe_data(old_properties=set()):
    """Scan through the pages of the trademe search scraping the property data."""

    print("Getting pages")
    pages = get_page_urls(settings.tm_url)

    print("Getting properties and filtering")
    properties = [prop for page_url in pages for prop in get_properties(page_url)]
    properties_filtered = [prop for prop in properties if prop["id"] not in old_properties]

    print("Getting property pages")
    property_pages = get_property_pages(properties_filtered)

    print("Got properties:")
    print("\n".join(prop['id'] for prop in properties_filtered))

    print("Processing properties")
    for prop, page in zip(properties_filtered, property_pages):
        print("Processing:", prop["id"])
        
        prop.update(get_property_table(page))

    return properties_filtered