"""
A module to scrape trademe for Hamilton housing stuff.


### To do ###

- [X] Bring in consequent pages on trademe search results.
- [ ] Update rather than overwrite Excel file.
- [X] Get RVs from council website
- [ ] Set up on launchd
- [ ] Put in threading
- [ ] Strip '-'s from strings
- [ ] Put urls in Excel file in links

"""
# coding: utf-8

from pprint import pprint
import requests
from bs4 import BeautifulSoup
import pandas
from rateslookup import get_rates

TM_SEARCH = r"https://www.trademe.co.nz/browse/categoryattributesearchresults.aspx?134=14&135=16&136=&153=&132=PROPERTY&122=3&122=5&49=400000&49=450000&29=&123=0&123=0&search=1&sidebar=1&cid=5748&rptpath=350-5748-"
TM_SITE = r"https://www.trademe.co.nz"
FIND_LINKS = {"class": "tmp-search-card-list-view__link"}
EXCEL_FILE = "Trademe Property List.xlsx"
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
]


def get_property_table(href):
    prop_details = requests.get(TM_SITE + href)
    prop_soup = BeautifulSoup(prop_details.text, "html.parser")
    listing_table = prop_soup.find(id="ListingAttributes")
    listing_table_rows = [row for row in listing_table.contents if row != "\n"]
    listing_dict = {}
    for p in listing_table_rows:
        key = p.contents[1].text.strip()
        value = p.contents[3].text.strip()
        listing_dict[key] = value
    return listing_dict


def get_href_id(prop):
    output = {}
    output["href"] = prop["href"]
    output["id"] = prop["id"]
    return output


def get_properties(bs_tree):
        properties = bs_tree.find_all(**FIND_LINKS)
        data = [get_href_id(prop) for prop in properties]
        for prop in data:
            print("Processing:", prop["id"])
            prop.update(get_property_table(prop["href"]))
        return data


if __name__ == "__main__":
    print("Getting properties")
    tm_request = requests.get(TM_SEARCH)
    html = tm_request.text
    html_bs = BeautifulSoup(html, "html.parser")

    properties_data = get_properties(html_bs)

    next_links = html_bs.find(id="PagingFooter")("a")[:-1]
    next_pages = [TM_SITE + a["href"] for a in next_links]

    for page in next_pages:
        page_request = requests.get(page)
        page_html = page_request.text
        page_bs = BeautifulSoup(page_html, "html.parser")
        page_data = get_properties(page_bs)
        properties_data += page_data


    print(f"Extracted {len(properties_data)} properties!")

    print("Getting rates")
    for prop in properties_data:
        loc = prop["Location:"]
        if "Rateable value (RV):" in prop:
            print("Already got rates value for ", loc)
            continue

        else:
            print("Getting RV for", loc)
            rates = get_rates(loc)
            prop["Rateable value (RV):"] = rates
            print("The RV amount is", rates)

    print("Saving file")
    tm_df = pandas.DataFrame(properties_data)
    tm_df_new_columns = tm_df.rename(
        lambda x: x.replace(":", ""), axis="columns"
    )


    tm_df_new_columns.to_excel(
        EXCEL_FILE,
        sheet_name="Properties",
        columns=COLUMNS_TO_KEEP,
        index=False,
    )
