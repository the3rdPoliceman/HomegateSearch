import argparse
import json
import os.path
import re
from math import ceil
import logging
import requests
from bs4 import BeautifulSoup

# Constants
HOMEGATE_PREFIX = "https://www.homegate.ch"
RESULT_CLASS = "ResultListHeader_locations_3uuG8"

# Set up logging
logging.basicConfig(level=logging.INFO)


def get_page_list(url_template, start_number, end_number):
    """Generates a list of page URLs based on a template and a range of page numbers."""
    page_list = []
    for page_number in range(start_number, end_number + 1):
        url_with_page = url_template.format(page=page_number)
        page_list.append(url_with_page)
    return page_list


def get_encoding(soup):
    """Extracts the encoding from a BeautifulSoup object."""
    encoding = soup.meta.get('charset')
    if encoding is None:
        encoding = soup.meta.get('content-type')
    if encoding is None:
        encoding = soup.meta.get('content')
    return encoding


def grab_page_content(url):
    """Requests a URL and returns its content and encoding."""
    try:
        page = requests.get(url)
        contents = page.content
        soup = BeautifulSoup(contents, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"Failed to grab page content: {e}")
        return None, None
    return contents, get_encoding(soup)


def get_property_links_from_page(contents):
    """Extracts property links from a page's HTML content."""
    soup = BeautifulSoup(contents, 'html.parser')
    pattern = re.compile(r'/mieten/\d{5,}')
    all_property_links = soup.find_all('a', href=pattern)
    return [property_link["href"].split("#")[0] for property_link in all_property_links]


def get_page_count(postcode, distance, url_template):
    """Determines the number of pages of results for a given postcode and distance."""
    url = url_template.format(postcode=postcode, distance=distance, page=1)
    contents, _ = grab_page_content(url)
    if contents is None:
        return 0
    soup = BeautifulSoup(contents, 'html.parser')
    result_count = soup.find('span', attrs={"class": RESULT_CLASS}).text
    match = re.match(r"(\d+) Treffer", result_count)
    results = int(match.group(1))
    return ceil(results/20)


def load_json(file_name):
    """Loads a JSON file or returns an empty list if the file does not exist."""
    if os.path.isfile(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return []


def write_json(file_name, data):
    """Writes data to a JSON file."""
    with open(file_name, 'w') as f:
        json.dump(data, f)


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('config', type=str, help='A JSON configuration file')
    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)

    url_template = config['url_template']
    postcodes = config['postcodes']
    distances = config['distances']
    search_terms = config['search_terms']
    possible_file = config['possible_file']
    rejected_file = config['rejected_file']

    rejected_urls = set(load_json(rejected_file))
    possible_urls = set(load_json(possible_file))

    all_page_list = []
    for postcode in postcodes:
        for distance in distances:
            logging.info(f"Searching postcode {postcode}, distance = {distance}")
            pages = get_page_count(postcode, distance, url_template)
            if pages > 0:
                page_list = get_page_list(url_template.replace('{postcode}', postcode).replace('{distance}', distance),
                                          1, pages)
                all_page_list.extend(page_list)

    all_property_links = []
    for page in all_page_list:
        logging.info(f"Getting {page}")
        content, _ = grab_page_content(page)
        if content is not None:
            property_links_from_page = get_property_links_from_page(content)
            all_property_links.extend([link for link in property_links_from_page if link not in all_property_links])

    for property_link in all_property_links:
        property_address = HOMEGATE_PREFIX + property_link
        if property_address in rejected_urls:
            logging.info(f"Skipping rejected URL: {property_address}")
            continue

        logging.info(f"Getting page for {property_address}")
        property_page_content, _ = grab_page_content(property_address)
        if property_page_content is not None:
            property_page_content = property_page_content.decode("utf-8")

            if any(term in property_page_content for term in search_terms):
                possible_urls.add(property_address)
            else:
                rejected_urls.add(property_address)

    write_json(possible_file, list(possible_urls))
    write_json(rejected_file, list(rejected_urls))


if __name__ == "__main__":
    main()
