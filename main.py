#!/usr/bin/env python3

"""
A module to scrape various sites for Hamilton housing stuff.


### To do ###

- [X] Bring in consequent pages on trademe search results.
- [x] Update rather than overwrite Excel file.
- [X] Get RVs from council website
- [x] Set up on launchd
- [x] Put in threading?
- [x] Strip '-'s from strings
- [x] Put urls in Excel file in links
- [ ] Parse dates properly
- [ ] Extract images

"""
# coding: utf-8

import grequests
import sys
from datetime import datetime

sys.path.append("/Users/timbledum/Documents/Python/tmhouse/") # Only required for launchd

from rateslookup import get_rates
import tmhouses
import tmexcel
import tmsales


if __name__ == "__main__":
    print("#" * 40 + "\n")
    print(sys.version)
    print("Getting properties", str(datetime.now()))

    tmexcel.create_workbook_if_not_present(
        {
            tmexcel.SHEET_NAME: tmexcel.COLUMNS_TO_KEEP,
            tmsales.SALES_SHEET: tmsales.COLUMNS,
        }
    )

    old_properties = tmexcel.get_previous_data_from_excel(
        sheet=tmexcel.SHEET_NAME, column=tmexcel.ID
    )
 
    properties_data = tmhouses.get_trademe_data(old_properties)

    print(f"Extracted {len(properties_data)} new properties!")

    print("Getting rates")
    for prop in properties_data:
        loc = prop["Location"]
        if "Rateable value (RV)" in prop:
            print("Already got rates value for", loc)
            continue

        else:
            print("Getting RV for", loc)
            rates = get_rates(loc)
            prop["Rateable value (RV)"] = rates
            print("The RV amount is", rates)

    print("Saving file")
    tmexcel.save_file(properties_data, tmexcel.SHEET_NAME, tmexcel.COLUMNS_TO_KEEP)

    print("Collecting sales prices")
    previous_sales = tmexcel.get_previous_data_from_excel(
        sheet=tmsales.SALES_SHEET, column=tmsales.ID
    )
    current_sales = tmsales.get_sale_prices()
    sales_to_save = [
        sale for sale in current_sales if sale[tmsales.COLUMNS[0]] not in previous_sales
    ]
    tmexcel.save_file(sales_to_save, tmsales.SALES_SHEET, tmsales.COLUMNS)

    print("Done!!!\n\n")
