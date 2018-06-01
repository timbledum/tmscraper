#!/usr/bin/env python3

"""
A module to scrape trademe for Hamilton housing stuff.


### To do ###

- [X] Bring in consequent pages on trademe search results.
- [x] Update rather than overwrite Excel file.
- [X] Get RVs from council website
- [x] Set up on launchd
- [ ] Put in threading
- [x] Strip '-'s from strings
- [x] Put urls in Excel file in links

"""
# coding: utf-8

import sys
from datetime import datetime
from pprint import pprint
import requests
from bs4 import BeautifulSoup

sys.path.append("/Users/timbledum/Documents/Python/tmhouse/")

from rateslookup import get_rates
import tmexcel

TM_SEARCH = r"https://www.trademe.co.nz/browse/categoryattributesearchresults.aspx?134=14&135=16&136=&153=&132=PROPERTY&122=3&122=5&49=400000&49=450000&29=&123=0&123=0&search=1&sidebar=1&cid=5748&rptpath=350-5748-"
TM_SITE = r"https://www.trademe.co.nz"
FIND_LINKS = {"class": "tmp-search-card-list-view__link"}


def get_property_table(href):
    prop_details = requests.get(TM_SITE + href)
    prop_soup = BeautifulSoup(prop_details.text, "html.parser")

    listing_table = prop_soup.find(id="ListingAttributes")
    listing_table_rows = [row for row in listing_table.contents if row != "\n"]

    listing_dict = {}
    for p in listing_table_rows:
        key = p.contents[1].text.strip().replace(":", "")
        value = p.contents[3].text.strip().replace("\xad", "")
        listing_dict[key] = value

    listing_date = prop_soup.find(id="PriceSummaryDetails_ListedStatusText")
    listing_dict["Listing date"] = listing_date.text[8:18].replace(
        ",", ""
    ) + " 18"

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
    print("Getting properties", str(datetime.now()))
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

    old_properties = tmexcel.get_current_ids()
    new_properties_data = [
        p for p in properties_data if p["id"] not in old_properties
    ]

    print(f"Extracted {len(new_properties_data)} new properties!")

    print("Getting rates")
    for prop in new_properties_data:
        loc = prop["Location"]
        if "Rateable value (RV)" in prop:
            print("Already got rates value for ", loc)
            continue

        else:
            print("Getting RV for", loc)
            rates = get_rates(loc)
            prop["Rateable value (RV)"] = rates
            print("The RV amount is", rates)

    print("Saving file")
    tmexcel.save_file(new_properties_data)
