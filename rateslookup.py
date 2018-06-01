"Module for looking up rates"
# coding: utf-8

import requests
from bs4 import BeautifulSoup

RATES_QUERY = "http://www.hamilton.govt.nz/our-services/property-and-rates/propertydatabase/Pages/default.aspx"


def split_property(prop):
    street_address = prop[:prop.find(", ")]
    return street_address.split(" ", maxsplit=1)


def get_rates(prop):

    number, street = split_property(prop)
    prop_params = {
        "searchType": "StreetAddress",
        "streetNumber": number,
        "streetName": street,
    }

    # get property link
    r = requests.get(RATES_QUERY, params=prop_params)
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
