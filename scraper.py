import re
from math import ceil

import requests
from bs4 import BeautifulSoup


def get_page_list(url, placeholder, start_number, end_number):
    page_list = []
    for page_number in range(start_number, end_number+1):
        url_with_page = url.replace(placeholder, str(page_number))
        page_list.append(url_with_page)

    return page_list


def get_encoding(soup):
    encoding = soup.meta.get('charset')
    if encoding == None:
        encoding = soup.meta.get('content-type')
    if encoding == None:
        encoding = soup.meta.get('content')

    return encoding


def grab_page_content(url):
    page = requests.get(url)
    contents = page.content
    soup = BeautifulSoup(contents, 'html.parser')

    return contents, get_encoding(soup)


def get_property_links_from_page(contents):
    soup = BeautifulSoup(contents, 'html.parser')
    pattern = re.compile(r'/mieten/\d{5,}')
    all_property_links = soup.find_all('a', href=pattern)
    property_links_list = list()

    for property_link in all_property_links:
        property_href = property_link["href"].split("#")[0]
        if property_href not in property_links_list:
            property_links_list.append(property_href)

    return property_links_list


def get_page_count(postcode, distance):
    postcode_template = "https://www.homegate.ch/mieten/parkplatz-garage/plz-%/trefferliste?be=!".replace("%", postcode).replace("!", distance)
    page = requests.get(postcode_template)
    contents = page.content
    soup = BeautifulSoup(contents, 'html.parser')
    result_count = soup.find('span', attrs={"class": "ResultListHeader_locations_3uuG8"}).text

    match = re.match(r"(\d+) Treffer", result_count)

    results = int(match.group(1))
    pages = ceil(results/20)

    print("found " + str(pages) + " pages for " + postcode)
    return pages


#postcode_list_full = ["8038", "8802", "8803", "8800", "8942", "8810", "8804", "8820", "8805", "8832", "8806", "8807", "8805", "8815", "8041", "8134", "8045", "8055", "8008", "8702", "8700", "8703", "8704", "8706", "8707", "8708", "8712", "8713", "8714", "8616", "8617", "8132", "8124"]
#distance_list_full = ["1000", "2000", "5000", "8000", "10000", "15000"]

postcode_list_full = ["8008"]
distance_list_full = ["1000"]

postcode_list = postcode_list_full
distance_list = distance_list_full

all_page_list = list()
for postcode in postcode_list:
    for distance in distance_list:
        print("searching postcode " + postcode + ", distance = " + distance)
        pages = get_page_count(postcode, distance)
        if pages > 0:
            page_list = get_page_list("https://www.homegate.ch/mieten/parkplatz-garage/plz-#/trefferliste?ep=%&be=!".replace("#", postcode).replace("!", distance), "%", 1, pages)
            for page in page_list:
                all_page_list.append(page)


all_property_links = list()
for page in all_page_list:
    print("getting " + page)
    content, encoding = grab_page_content(page)
    property_links_from_page = get_property_links_from_page(content)
    for property_link in property_links_from_page:
        if property_link not in all_property_links:
            all_property_links.append(property_link)


possible_places = set()
for index,property_link in enumerate(all_property_links):
    homegate_prefix = "https://www.homegate.ch"
    property_address = homegate_prefix + property_link
    print("getting page for " + property_address)
    property_page_content, encoding = grab_page_content(property_address)
    property_page_content = property_page_content.decode("utf-8")

    if "wohnwagen" in property_page_content or "wohnmobile" in property_page_content:
        possible_places.add(property_address)
        filename = "possible_" + str(index) + ".txt"
        with open(filename, "w") as text_file:
            text_file.write(property_address + " " + property_page_content)
    else:
        filename = "rejected_" + str(index) + ".txt"
        with open(filename, "w") as text_file:
            text_file.write(property_address + " " + property_page_content)


for possible_place in possible_places:
    print("possible place" + possible_place)


