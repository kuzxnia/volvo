import logging
from price_parser import Price

import util

logging.basicConfig(filename='data/volvo.log', format='%(asctime)s : %(levelname)s : %(name)s : %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

output_filename = 'data/volvoc30.json'

# wejscie - marka model zapis
# approx pojemność
# regex z opisu ogłoszenia
#


def update_links():
    links = util.read_json_from_file(output_filename)
    updated_links = extract_offers_links(url='https://www.otomoto.pl/osobowe/volvo/c30/', links=links)
    log.info('links fetched succesfully %s', len(updated_links))
    util.write_json_to_file(output_filename, updated_links)


def fetch_offers_details():
    links = util.read_json_from_file(output_filename)
    log.info('\nstarting offer fetch, %s to go', len(links))

    succesful = 0
    for item_chunk in util.chunks([link for link in links if link['Fetched'] is False], 5):
        for i, item in enumerate(item_chunk):
            link = item['Link']
            page = util.parse_page(link)
            try:
                data = extract_offer_details(page)
                item.update(data)
                succesful += 1
            except:
                log.error('extracting details from page faild url=%s', link, exc_info=True)
        log.info('pages parsed succesfully %s, unsuccesfull %s', succesful, len(links) - succesful)

        log.info('pages parsed succesfully %s, unsuccesfull %s', succesful, len(links) - succesful)
        util.write_json_to_file(output_filename, links)

    log.info('pages parsed succesfully %s, unsuccesfull %s', succesful, len(links) - succesful)
    util.write_json_to_file(output_filename, links)


def extract_offers_links(url=None, page=None, links=None):
    assert not (url is None and page is None), 'page or url required'

    if not page:
        page = util.parse_page(url)
    if not links:
        links = []

    links_from_page = [
        {'Id': selection["data-ad-id"], 'Fetched': False, 'Link': selection["href"]}
        for selection in page.find_all("a", {"class": "offer-title__link"})
        if not util.find(links, lambda x: x['Link'] == selection["href"])
    ]

    log.info('links extracted %s', len(links_from_page))
    if next_page_url := page.find('li', {"class": "next abs"}):
        next_page_url = next_page_url.find('a')['href']

        log.info('next_page_url %s', next_page_url)
        return extract_offers_links(url=next_page_url, links=links_from_page + links)
    else:
        return links_from_page + links


def extract_offer_details(page):
    result = {}
    for section in page.find("div", {"class": "parametersArea"}).find_all("li"):

        if selections := util.parse_selection(2, section.find('span'), section.find('div')):
            label, value = selections
            result[label] = value

    extra = []
    for section in page.find("div", {"class": "offer-features"}).find_all("li"):
        extra.extend(util.parse_selection(0, section.contents))

    result.update({label: True for label in extra})
    # pojemność skokowa

    result['Opis'], result['Cena'], result['Waluta'] = util.format_selection(
        page.find("div", {"class": "offer-description__description"}),
        page.find("span", {"class": "offer-price__number"}),
        page.find("span", {"class": "offer-price__currency"})
    )
    result['Cena'] = Price.fromstring(result['Cena'])
    result['Fetched'] = True
    return result


if __name__ == "__main__":
    fetch_offers_details()
    # update_links()
