import logging
from contextlib import contextmanager
import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
import time
import random
import pandas as pd


log = logging.getLogger(__name__)


def parse_page(url, throught_proxy=True, timeout=2, timedelay=1):
    """
    Raises:
        requests.exceptions.RequestException
    """
    if timedelay:
        delay = random.randint(timedelay, timedelay+3)
        log.info('waiting %ss' % delay)
        time.sleep(delay)

    page, trys = None, 0
    while not page and trys < 10:
        trys += 1
        try:
            page = requests.get(url, timeout=timeout)
            page.raise_for_status()
        except:
            log.info('request error, waiting 5s')
            time.sleep(5)

    log.info("Page Fetched")
    return bs(page.text, "lxml")


def chunks(lst, chunk_size):
    if chunk_size < 2:
        return lst
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_selection(*selections):
    result = []
    for i, selection in enumerate(selections):
        if isinstance(selection, tuple):
            selection = selection[0]
        if not isinstance(selection, str):
            selection = selection.text

        if striped_selection := selection.replace("\n", "").replace("\t", "").strip():
            result.append(striped_selection)

    return result


def parse_selection(n, *selections):
    result = []
    for selection in chunks(selections, n):
        if None in (selection):
            continue
        result.extend(format_selection(*selection))
    return result


def find(iterable, condition):
    for item in (x for x in iterable if condition(x)):
        return item
    return None


def fetch_page_to_file(url, filename):
    page = parse_page(url)
    with open(filename, 'w') as file:
        file.write(str(page))
        log.info('page writed successfully')


def read_page_from_file(filename):
    return bs(open(filename, 'r').read(), "lxml")


def read_json_from_file(filename):
    with open(filename) as file:
        data = json.load(file)

    return data


def write_json_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

def read_json_as_df(filename):
    return pd.read_json(filename)
