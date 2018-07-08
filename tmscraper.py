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
import tmsales
from settings import settings

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
    listing_dict["Date listed"] = listing_date.text[8:18].replace(
        ",", ""
    ) + " 18"

    return listing_dict


def get_href_id(prop):
    output = {}
    output["href"] = prop["href"]
    output["id"] = prop["id"]
    return output


def get_properties(bs_tree, old_properties):
    properties = bs_tree.find_all(**FIND_LINKS)
    data = [get_href_id(prop) for prop in properties]
    data_filtered = [prop for prop in data if prop['id'] not in old_properties]

    for prop in data_filtered:
        print("Processing:", prop["id"])
        prop.update(get_property_table(prop["href"]))
    return data_filtered


if __name__ == "__main__":
    print("#" * 40 + "\n")
    print("Getting properties", str(datetime.now()))
    tm_request = requests.get(settings.tm_url)
    html = tm_request.text
    html_bs = BeautifulSoup(html, "html.parser")

    tmexcel.create_workbook_if_not_present()
    old_properties = tmexcel.get_current_ids()
    properties_data = get_properties(html_bs, old_properties)

    next_links = html_bs.find(id="PagingFooter")("a")[:-1]
    next_pages = [TM_SITE + a["href"] for a in next_links]

    for number, page in enumerate(next_pages):
        print("Processing page", number + 2)
        page_request = requests.get(page)
        page_html = page_request.text
        page_bs = BeautifulSoup(page_html, "html.parser")
        page_data = get_properties(page_bs, old_properties)
        properties_data += page_data

    print(f"Extracted {len(properties_data)} new properties!")

    print("Getting rates")
    for prop in properties_data:
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
    tmexcel.save_file(properties_data)

    print('Collecting sales prices')
    tmsales.process_sales()

    print('Done!!!\n\n')