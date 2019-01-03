# Trademe property scraper

A script that creates and maintains a list of all properties listed on Trademe using the specified search.

It has evolved to extract rates valuations (Hamilton only) and sales data.

## Installation instructions

Ensure that [python 3.6](https://www.python.org/downloads/) is installed (if on Windows,
I suggest checking the box that says "Add Python to PATH" - this enables you to use `python` and `pip` on the windows command line.

### Dependencies

The third party dependencies are as follows - you need to install these.

- requests
- grequests
- beautifulsoup4
- pyaml
- openpyxl
- python-dateutil

Install these with `pip install` (i.e. `pip install openpyxl`).

Or just run the following command at the command line:

    pip install requests grequests beautifulsoup4 pyaml openpyxl python-dateutil

### Update settings

You will need to update the seetings.yaml file to update some of the values to your computer. You will need to edit:

- module_address
- excel_file_address
- tm_url (optional - you can go to trademe, do the search you want, then copy-paste the url here to modify the search criteria)

The full paths of various files are included in order to ensure that this script can be scheduled by your platforms task scheduler.

## Running th file

Start the script by typing `python main.py`.
