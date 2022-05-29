import logging
import pickle
from time import sleep
from tkinter import Tk

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from persistence import set_document_to_firestore, get_documents_from_firestore
from util import wait

HOST_URL = "https://dl.acm.org"
JOURNAL_COLLECTION = "journal-publications"
CITATION_COLLECTION = "journal-citations"

logging.basicConfig(filename='citation_scrapper.log', level=logging.INFO)
logger = logging.getLogger()
bibtext_raw_logger = logging.getLogger()
bibtext_json_logger = logging.getLogger()

already_done_journals_issues = ['/toc/csur/2018/50/6']


@wait(15)
def click_element(element, driver):
    logger.info(f'clicking element: {element}')
    print(f'clicking element: {element}')
    webdriver.ActionChains(driver).move_to_element(element).click(element).perform()


def create_parser():
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = True
    parser.homogenise_fields = False
    return parser


def parse_bibtext_to_json(parser, bibtext_raw_str: str):
    try:
        bib_database = bibtexparser.loads(bibtext_raw_str, parser=parser)
        return bib_database
    except Exception as e:
        print(f'Could not parse bibtext to json: {e}')
        logger.warning(f'Could not parse bibtext to json: {e}')
        return None


@wait(15)
def click_wrapper(element):
    element.click()


def collect_all_citations():
    publications = get_documents_from_firestore(JOURNAL_COLLECTION)
    for p in publications:
        journal_publication_data = p.get().to_dict()
        journal = journal_publication_data.get("journal")
        link = journal_publication_data.get("link")
        if link not in already_done_journals_issues:
            collect_citations_for_journal_issue(journal, link)
            already_done_journals_issues.append(link)
            print(f'done with: {already_done_journals_issues}')
            print_and_pickle_all_already_scrapped_entries()
        else:
            print(f'already done with {link}')


def print_and_pickle_all_already_scrapped_entries():
    print(*already_done_journals_issues, sep=' ')
    pickle.dump(already_done_journals_issues, open("save.p", "wb"))


@wait(120)
def collect_citations_for_journal_issue(journal: str, journal_publication_link: str):
    parser = create_parser()

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    url = f'{HOST_URL}{journal_publication_link}'
    print(url)
    driver.get(url)  # url associated with button click
    # driver.get(f'file:///C:/Users/Jasper/Desktop/tst/JACM_%20Vol69No1.html')  # url associated with button click
    elements = driver.find_elements(By.XPATH,
                                    "//li/a[@class='btn--icon simple-tooltip__block--b'][@aria-label='Export Citation']")

    print(f'found {len(elements)} citations')

    for count, element in enumerate(elements):
        logger.info(f'element: {element}')
        # click_element(element, driver)  # clicks on citation icon
        click_wrapper(element)
        sleep(5)
        cpy_to_clipboard_btn = driver.find_element(By.XPATH,
                                                   "//a[@class='copy__btn'][@title='Copy citation'][@role='menuitem']")
        # click_element(cpy_to_clipboard_btn, driver)  # copy on "to clipboard" button
        click_wrapper(cpy_to_clipboard_btn)
        sleep(5)  # wait a bit longer to ensure the citation text is loaded

        bibtext_raw_str = Tk().clipboard_get()
        logger.info(bibtext_raw_str)
        bibtext_raw_logger.info(bibtext_raw_str)

        bib_db = parse_bibtext_to_json(parser, bibtext_raw_str)
        save_newest_citation(bib_db, journal, journal_publication_link, count)

        # click_element(driver.find_element(By.TAG_NAME, "body"))  # click on body, leave citation view
        click_wrapper(driver.find_element(By.TAG_NAME, "body"))
        sleep(5)


def save_newest_citation(db: BibDatabase, journal: str, edition: str, n: int):
    if db is None:
        logger.warning(f'Could not save citation as bibDatabase is None')
        return
    if len(db.entries) < 1:
        logger.warning(f'Could not save citation as bibDatabase is Empty')
        return
    try:
        e = db.entries[-1]
        bibtext_json_logger.info(e)
        set_document_to_firestore(key=f'{journal}-{edition.replace("/", "")}-{n}',
                                  data=e,
                                  collection=CITATION_COLLECTION,
                                  merge=True)
    except Exception as e:
        print(f'Could not save citation to firestore: {e}')
        logger.warning(f'Could not save citation to firestore: {e}')


def test_bibtext_parser():
    bibtex = """@STRING{ jean = "Jean"}

    @ARTICLE{Cesar2013,
      author = jean # { César},
      title = {An amazing title},
      year = {2013},
      month = jan,
      volume = {12},
      pages = {12--23},
      journal = {Nice Journal},
    }
    """

    bibtex2 = """@STRING{ jeff = "asda"}

    @ARTICLE{Cesar2013,
      author = jean # { asd},
      title = {An asd title},
      year = {2013},
      month = feb,
      volume = {34},
      pages = {12--65},
      journal = {Nice Cocktails},
    }
    """
    p = create_parser()
    parse_bibtext_to_json(p, bibtex)
    db = parse_bibtext_to_json(p, bibtex2)
    save_newest_citation(db)


if __name__ == '__main__':
    print("starting citation scrapping")
    collect_all_citations()
