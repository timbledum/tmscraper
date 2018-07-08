# coding: utf-8
"""Module for looking up rates from Hamilton council website."""

import requests
from bs4 import BeautifulSoup
from settings import settings


def split_property(prop):
    """Extract key street address information from the full address."""
    street_address = prop[: prop.find(", ")]
    return street_address.split(" ", maxsplit=1)


def get_rates(prop):
    """Scrape the rates information from the Hamilton Council website."""
    number, street = split_property(prop)
    prop_params = {
        "searchType": "StreetAddress",
        "streetNumber": number,
        "streetName": street,
    }

    # get property link
    r = requests.get(settings.rates_url, params=prop_params)
    r_bs = BeautifulSoup(r.text, "html.parser")
    results = r_bs.find(attrs={"class": "form-results"})

    try:
        link = results.find("a")["href"]
    except TypeError:
        print("No RV found :(")
        return "No RV found."

    # get rates value
    prop = requests.get(link)
    rates_bs = BeautifulSoup(prop.text, "html.parser")
    label = rates_bs.find(string="Capital value")
    rates = label.next_element.next_element.text

    return rates
