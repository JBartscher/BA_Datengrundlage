import codecs
import re

import requests

from persistence import set_document_to_firestore
from util import wait, timestamp

from bs4 import BeautifulSoup
import logging

HOST_URL = "https://dl.acm.org/"

all_journals = ["csur", "cola", "dlt", "jats", "dgov", "dtrap", "fac", "health", "imwut", "jacm", "jdiq", "jea", "jetc",
                "jocch", "jrc", "pacmcgit", "pacmhci", "pacmpl", "pomacs", "taas", "taccess", "taco", "talg", "tallip",
                "tap", "taslp", "tcbb", "tcps", "tds", "teac", "tecs", "telo", "thri", "tiis", "tiot", "tist", "tkdd",
                "tmis", "toce", "tochi", "tocl", "tocs", "toct", "todaes", "tods", "tog", "tois", "toit", "tomacs",
                "tomm",
                "tompecs", "toms", "ton", "topc", "toplas", "tops", "tors", "tos", "tosem", "tosn", "tqc", "trets",
                "tsas",
                "tsc", "tweb"]  # 65

uninitiated_journals = ['topc', 'tosem', 'jats', 'trets', 'jrc', 'tsas', 'dlt', 'tqc', 'tosn', 'tompecs', 'toplas',
                        'tweb', 'cola', 'tos', 'tops', 'ton', 'tsc', 'toms', 'tors']  # 19

journals_with_archive = ['csur', 'dgov', 'dtrap', 'fac', 'health', 'imwut', 'jacm', 'jdiq', 'jea', 'jetc', 'jocch',
                         'pacmcgit', 'pacmhci', 'pacmpl', 'pomacs', 'taas', 'taccess', 'taco', 'talg', 'tallip', 'tap',
                         'taslp', 'tcbb', 'tcps', 'tds', 'teac', 'tecs', 'telo', 'thri', 'tiis', 'tiot', 'tist', 'tkdd',
                         'tmis', 'toce', 'tochi', 'tocl', 'tocs', 'toct', 'todaes', 'tods', 'tog', 'tois', 'toit',
                         'tomacs', 'tomm']  # 46/46 Done

logging.basicConfig(filename='output.log', level=logging.INFO)
logger = logging.getLogger()


@wait(120)
def collect_links_of_publications_of_year_in_decade(journal_name: str, decade: int, year: int):
    url = f'{HOST_URL}loi/{journal_name}/group/d{decade}.y{year}'
    page = requests.get(url, timeout=None)
    if page.status_code == 200:
        soup = soupify_HTML_content(page.content)
        links = soup.find_all('a', attrs={'class': 'loi__issue', 'href': re.compile(f'{year}')})
        logger.info(f'found {len(links)} journal-links in year {year}')
        for count, link in enumerate(links):
            logger.info(f'found: {link}')
            if link.has_attr('href'):
                href = link['href']
                set_document_to_firestore(key=f'{journal_name}-{year}-{decade}-{count}',
                                          data={
                                              "link": href,
                                              "journal": journal_name,
                                              "decade": decade,
                                              "year": year,
                                              "last-updated": timestamp()
                                          },
                                          collection="journal-publications",
                                          merge=True)
            else:
                logger.warning(f'could not find href attribute for PageElement {link}')
    else:
        logger.warning(
            f'cannot get year {year} from decade {decade} of journal {journal_name}. Received {page.status_code} status code')


@wait(120)
def has_archive(journal_name):
    url = f'{HOST_URL}loi/{journal_name}'
    page = requests.get(url, timeout=None)
    logger.info(f'{page.status_code} for {journal_name}')
    if page.status_code == 200:
        soup = soupify_HTML_content(page.content)
        year_container = soup.find_all("ul", attrs={"role": "tablist", "class": "loi__list"})
        logger.debug(year_container)
        if len(year_container) > 0:
            logger.info(f"{journal_name} has archive")
            return True  # has Archive
        logger.info(f"{journal_name} has no archive")
        return False  # has no Archive
    logger.info(f"{journal_name} has no archive")
    return False  # cant access


@wait(120)
def has_2010s(journal_name):
    url = f'{HOST_URL}loi/{journal_name}/group/d2010.y2019'
    page = requests.get(url, timeout=None)
    logger.info(f'{page.status_code} for {journal_name}')
    if page.status_code == 200:
        soup = soupify_HTML_content(page.content)
        year_container = soup.find_all("a", attrs={"data-url": "d2010", "title": "2010s"})
        if len(year_container) > 0:
            return True  # has 2010-2019
        return False  # has no 2010-2019


@wait(120)
def has_2020s(journal_name: str):
    url = f'{HOST_URL}loi/{journal_name}/group/d2010.y2019'
    page = requests.get(url, timeout=None)
    print(f'{page.status_code} for {journal_name}')
    if page.status_code == 200:
        soup = soupify_HTML_content(page.content)
        year_container = soup.find_all("a", attrs={"data-url": "d2020", "title": "2020s"})
        if len(year_container) > 0:
            return True  # has 2010-2019
        return False  # has no 2010-2019


def soupify_HTML_content(content):
    return BeautifulSoup(content, 'html.parser')


def collect_links_of_journal(journal_name: str):
    if has_2010s(journal_name):
        collect_links_of_publications_of_year_in_decade(journal_name, 2010, 2018)
        logger.info("FINISHED 2018")
        collect_links_of_publications_of_year_in_decade(journal_name, 2010, 2019)
        logger.info("FINISHED 20119")
    if has_2020s(journal_name):
        collect_links_of_publications_of_year_in_decade(journal_name, 2020, 2020)
        logger.info("FINISHED 2020")
        collect_links_of_publications_of_year_in_decade(journal_name, 2020, 2021)
        logger.info("FINISHED 2021")
        collect_links_of_publications_of_year_in_decade(journal_name, 2020, 2022)
        logger.info("FINISHED 2022")


def collect_all_journal_links(journals: list):
    for journal in journals:
        try:
            collect_links_of_journal(journal)
        except Exception as e:
            logger.error(f'could not collect all links of {journal}: {e}')
    logger.info("????DONE WITH THE COLLECTION!????")


def test_with_local_file():
    page = codecs.open("C:/Users/Jasper/Desktop/tst/JACMArchive.html", 'r', 'utf-8')
    soup = soupify_HTML_content(page)
    links = soup.find_all('a', attrs={'class': 'loi__issue', 'href': re.compile(r'2022')})
    for l in links:
        print(l.getText())
        print(l.has_attr('href'))
        print(l['href'])


if __name__ == '__main__':
    print(len(journals_with_archive))
    collect_all_journal_links(journals_with_archive)
