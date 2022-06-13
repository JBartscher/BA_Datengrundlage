import logging
import pickle
from time import sleep
from tkinter import Tk

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from persistence import set_document_to_firestore, get_documents_from_firestore
from util import wait, timestamp

HOST_URL = "https://dl.acm.org"
JOURNAL_COLLECTION = "journal-publications"
CITATION_COLLECTION = "journal-citations"

logging.basicConfig(filename='citation_scrapper.log', level=logging.INFO)
logger = logging.getLogger()
bibtext_raw_logger = logging.getLogger()
bibtext_json_logger = logging.getLogger()

already_done_journals_issues = ['/toc/csur/2018/50/6', '/toc/csur/2018/50/5', '/toc/csur/2018/50/4',
                                '/toc/csur/2018/50/3', '/toc/csur/2018/50/2', '/toc/csur/2018/50/1',
                                '/toc/csur/2019/51/6', '/toc/csur/2019/51/5', '/toc/csur/2019/51/4',
                                '/toc/csur/2019/51/3', '/toc/csur/2019/51/2', '/toc/csur/2019/51/1',
                                '/toc/csur/2020/52/6', '/toc/csur/2020/52/5', '/toc/csur/2020/52/4',
                                '/toc/csur/2020/52/3', '/toc/csur/2020/52/2', '/toc/csur/2020/52/1',
                                '/toc/csur/2021/53/6', '/toc/csur/2021/53/5', '/toc/csur/2021/53/4',
                                '/toc/csur/2021/53/3', '/toc/csur/2021/53/2', '/toc/csur/2021/53/1',
                                '/toc/csur/2022/54/9', '/toc/csur/2022/54/8', '/toc/csur/2022/54/7',
                                '/toc/csur/2022/54/6', '/toc/csur/2022/54/5', '/toc/csur/2022/54/4',
                                '/toc/csur/2022/54/3', '/toc/csur/2022/54/2', '/toc/csur/2022/54/1',
                                '/toc/dgov/2020/1/4', '/toc/dgov/2020/1/3', '/toc/dgov/2020/1/2', '/toc/dgov/2020/1/1',
                                '/toc/dgov/2021/2/4', '/toc/dgov/2021/2/3', '/toc/dgov/2021/2/2', '/toc/dgov/2021/2/1',
                                '/toc/dgov/2022/3/1', '/toc/dtrap/2020/1/4', '/toc/dtrap/2020/1/3',
                                '/toc/dtrap/2020/1/2', '/toc/dtrap/2020/1/1', '/toc/dtrap/2021/2/4',
                                '/toc/dtrap/2021/2/3', '/toc/dtrap/2021/2/2', '/toc/dtrap/2021/2/1',
                                '/toc/dtrap/2022/3/2', '/toc/dtrap/2022/3/1', '/toc/fac/2018/30/6',
                                '/toc/fac/2018/30/5', '/toc/fac/2018/30/3-4', '/toc/fac/2018/30/2',
                                '/toc/fac/2018/30/1', '/toc/fac/2019/31/6', '/toc/fac/2019/31/5', '/toc/fac/2019/31/4',
                                '/toc/fac/2019/31/3', '/toc/fac/2019/31/2', '/toc/fac/2019/31/1',
                                '/toc/fac/2020/32/4-6', '/toc/fac/2020/32/2-3', '/toc/fac/2020/32/1',
                                '/toc/fac/2021/33/6', '/toc/fac/2021/33/4-5', '/toc/fac/2021/33/3',
                                '/toc/fac/2021/33/2', '/toc/fac/2021/33/1', '/toc/health/2020/1/4',
                                '/toc/health/2020/1/3', '/toc/health/2020/1/2', '/toc/health/2020/1/1',
                                '/toc/health/2021/2/4', '/toc/health/2021/2/3', '/toc/health/2021/2/2',
                                '/toc/health/2021/2/1', '/toc/health/2022/3/3', '/toc/health/2022/3/2',
                                '/toc/health/2022/3/1', '/toc/imwut/2018/2/4', '/toc/imwut/2018/2/3',
                                '/toc/imwut/2018/2/2', '/toc/imwut/2018/2/1', '/toc/imwut/2018/1/4',
                                '/toc/imwut/2019/3/4', '/toc/imwut/2019/3/3', '/toc/imwut/2019/3/2',
                                '/toc/imwut/2019/3/1', '/toc/imwut/2020/4/4', '/toc/imwut/2020/4/3',
                                '/toc/imwut/2020/4/2', '/toc/imwut/2020/4/1', '/toc/imwut/2021/5/4',
                                '/toc/imwut/2021/5/3', '/toc/imwut/2021/5/2', '/toc/imwut/2021/5/1',
                                '/toc/imwut/2022/6/1', '/toc/jacm/2018/65/6', '/toc/jacm/2018/65/5',
                                '/toc/jacm/2018/65/4', '/toc/jacm/2018/65/3', '/toc/jacm/2018/65/2',
                                '/toc/jacm/2018/65/1', '/toc/jacm/2019/66/6', '/toc/jacm/2019/66/5',
                                '/toc/jacm/2019/66/4', '/toc/jacm/2019/66/3', '/toc/jacm/2019/66/2',
                                '/toc/jacm/2019/66/1', '/toc/jacm/2020/67/6', '/toc/jacm/2020/67/5',
                                '/toc/jacm/2020/67/4', '/toc/jacm/2020/67/3', '/toc/jacm/2020/67/2',
                                '/toc/jacm/2020/67/1', '/toc/jacm/2021/68/6', '/toc/jacm/2021/68/5',
                                '/toc/jacm/2021/68/4', '/toc/jacm/2021/68/3', '/toc/jacm/2021/68/2',
                                '/toc/jacm/2021/68/1', '/toc/jacm/2022/69/2', '/toc/jacm/2022/69/1',
                                '/toc/jdiq/2018/10/4', '/toc/jdiq/2018/10/3', '/toc/jdiq/2018/10/2',
                                '/toc/jdiq/2018/10/1', '/toc/jdiq/2019/11/4', '/toc/jdiq/2019/11/3',
                                '/toc/jdiq/2019/11/2', '/toc/jdiq/2019/11/1', '/toc/jdiq/2020/12/4',
                                '/toc/jdiq/2020/12/3', '/toc/jdiq/2020/12/2', '/toc/jdiq/2020/12/1',
                                '/toc/jdiq/2021/13/4', '/toc/jdiq/2021/13/3', '/toc/jdiq/2021/13/2',
                                '/toc/jdiq/2021/13/1', '/toc/jdiq/2022/14/2', '/toc/jdiq/2022/14/1',
                                '/toc/jetc/2018/14/4', '/toc/jetc/2018/14/3', '/toc/jetc/2018/14/2',
                                '/toc/jetc/2018/14/1', '/toc/jetc/2019/15/4', '/toc/jetc/2019/15/3',
                                '/toc/jetc/2019/15/2', '/toc/jetc/2019/15/1', '/toc/jetc/2020/16/4',
                                '/toc/jetc/2020/16/3', '/toc/jetc/2020/16/2', '/toc/jetc/2020/16/1',
                                '/toc/jetc/2021/17/4', '/toc/jetc/2021/17/3', '/toc/jetc/2021/17/2',
                                '/toc/jetc/2021/17/1', '/toc/jetc/2022/18/3', '/toc/jetc/2022/18/2',
                                '/toc/jetc/2022/18/1', '/toc/jocch/2018/11/4', '/toc/jocch/2018/11/3',
                                '/toc/jocch/2018/11/2', '/toc/jocch/2018/11/1', '/toc/jocch/2019/12/3',
                                '/toc/jocch/2019/12/2', '/toc/jocch/2019/12/1', '/toc/jocch/2020/13/4',
                                '/toc/jocch/2020/13/3', '/toc/jocch/2020/13/2', '/toc/jocch/2020/13/1',
                                '/toc/jocch/2020/12/4', '/toc/jocch/2021/14/4', '/toc/jocch/2021/14/3',
                                '/toc/jocch/2021/14/2', '/toc/jocch/2021/14/1', '/toc/jocch/2022/15/2',
                                '/toc/jocch/2022/15/1', '/toc/pacmcgit/2018/1/2', '/toc/pacmcgit/2018/1/1',
                                '/toc/pacmcgit/2019/2/2', '/toc/pacmcgit/2019/2/1', '/toc/pacmcgit/2020/3/2',
                                '/toc/pacmcgit/2020/3/1', '/toc/pacmcgit/2021/4/3', '/toc/pacmcgit/2021/4/2',
                                '/toc/pacmcgit/2021/4/1', '/toc/pacmcgit/2022/5/2', '/toc/pacmcgit/2022/5/1',
                                '/toc/pacmhci/2018/2/CSCW', '/toc/pacmhci/2018/2/EICS', '/toc/pacmhci/2019/3/GROUP',
                                '/toc/pacmhci/2019/3/CSCW', '/toc/pacmhci/2019/3/EICS', '/toc/pacmhci/2020/4/ISS',
                                '/toc/pacmhci/2020/4/CSCW2', '/toc/pacmhci/2020/4/EICS', '/toc/pacmhci/2020/4/CSCW1',
                                '/toc/pacmhci/2020/4/GROUP', '/toc/pacmhci/2021/5/ISS', '/toc/pacmhci/2021/5/CSCW2',
                                '/toc/pacmhci/2021/5/CHI+PLAY', '/toc/pacmhci/2021/5/GROUP', '/toc/pacmhci/2021/5/EICS',
                                '/toc/pacmhci/2021/5/CSCW1', '/toc/pacmhci/2021/4/CSCW3', '/toc/pacmhci/2022/6/ETRA',
                                '/toc/pacmhci/2022/6/CSCW1', '/toc/pacmhci/2022/6/GROUP', '/toc/pacmpl/2018/2/OOPSLA',
                                '/toc/pacmpl/2018/2/ICFP', '/toc/pacmpl/2018/2/POPL', '/toc/pacmpl/2019/3/OOPSLA',
                                '/toc/pacmpl/2019/3/ICFP', '/toc/pacmpl/2019/3/POPL', '/toc/pacmpl/2020/4/OOPSLA',
                                '/toc/pacmpl/2020/4/ICFP', '/toc/pacmpl/2020/4/HOPL', '/toc/pacmpl/2020/4/POPL',
                                '/toc/pacmpl/2021/5/OOPSLA', '/toc/pacmpl/2021/5/ICFP', '/toc/pacmpl/2021/5/POPL',
                                '/toc/pacmpl/2022/6/OOPSLA1', '/toc/pacmpl/2022/6/POPL', '/toc/pomacs/2018/2/3',
                                '/toc/pomacs/2018/2/2', '/toc/pomacs/2018/2/1', '/toc/pomacs/2019/3/3',
                                '/toc/pomacs/2019/3/2', '/toc/pomacs/2019/3/1', '/toc/pomacs/2020/4/3',
                                '/toc/pomacs/2020/4/2', '/toc/pomacs/2020/4/1', '/toc/pomacs/2021/5/3',
                                '/toc/pomacs/2021/5/2', '/toc/pomacs/2021/5/1', '/toc/pomacs/2022/6/1',
                                '/toc/taas/2018/13/4', '/toc/taas/2018/13/3', '/toc/taas/2018/13/2',
                                '/toc/taas/2018/13/1', '/toc/taas/2020/15/4', '/toc/taas/2020/15/3',
                                '/toc/taas/2020/15/2', '/toc/taas/2020/15/1', '/toc/taas/2021/16/2',
                                '/toc/taas/2021/16/1', '/toc/taccess/2018/11/4', '/toc/taccess/2018/11/3',
                                '/toc/taccess/2018/11/2', '/toc/taccess/2018/11/1', '/toc/taccess/2019/12/4',
                                '/toc/taccess/2019/12/3', '/toc/taccess/2019/12/2', '/toc/taccess/2019/12/1',
                                '/toc/taccess/2020/13/4', '/toc/taccess/2020/13/3', '/toc/taccess/2020/13/2',
                                '/toc/taccess/2020/13/1', '/toc/taccess/2021/14/4', '/toc/taccess/2021/14/3',
                                '/toc/taccess/2021/14/2', '/toc/taccess/2021/14/1', '/toc/taccess/2022/15/2',
                                '/toc/taccess/2022/15/1', '/toc/taco/2018/15/4', '/toc/taco/2018/15/3',
                                '/toc/taco/2018/15/2', '/toc/taco/2018/15/1', '/toc/taco/2019/16/4',
                                '/toc/taco/2019/16/3', '/toc/taco/2019/16/2', '/toc/taco/2019/16/1',
                                '/toc/taco/2020/17/4', '/toc/taco/2020/17/3', '/toc/taco/2020/17/2',
                                '/toc/taco/2020/17/1', '/toc/taco/2021/18/4', '/toc/taco/2021/18/3',
                                '/toc/taco/2021/18/2', '/toc/taco/2021/18/1', '/toc/taco/2022/19/3',
                                '/toc/taco/2022/19/2', '/toc/taco/2022/19/1', '/toc/talg/2018/14/4',
                                '/toc/talg/2018/14/3', '/toc/talg/2018/14/2', '/toc/talg/2018/14/1',
                                '/toc/talg/2019/15/4', '/toc/talg/2019/15/3', '/toc/talg/2019/15/2',
                                '/toc/talg/2019/15/1', '/toc/talg/2020/16/4', '/toc/talg/2020/16/3',
                                '/toc/talg/2020/16/2', '/toc/talg/2020/16/1', '/toc/talg/2021/17/4',
                                '/toc/talg/2021/17/3', '/toc/talg/2021/17/2', '/toc/talg/2021/17/1',
                                '/toc/talg/2022/18/2', '/toc/talg/2022/18/1', '/toc/tallip/2018/17/4',
                                '/toc/tallip/2018/17/3', '/toc/tallip/2018/17/2', '/toc/tallip/2018/17/1',
                                '/toc/tallip/2019/18/4', '/toc/tallip/2019/18/3', '/toc/tallip/2019/18/2',
                                '/toc/tallip/2019/18/1', '/toc/tallip/2020/19/6', '/toc/tallip/2020/19/5',
                                '/toc/tallip/2020/19/4', '/toc/tallip/2020/19/3', '/toc/tallip/2020/19/2',
                                '/toc/tallip/2020/19/1', '/toc/tallip/2021/20/6', '/toc/tallip/2021/20/5',
                                '/toc/tallip/2021/20/4', '/toc/tallip/2021/20/3', '/toc/tallip/2021/20/2',
                                '/toc/tallip/2021/20/1', '/toc/tallip/2022/21/5', '/toc/tallip/2022/21/4',
                                '/toc/tallip/2022/21/3', '/toc/tallip/2022/21/2', '/toc/tallip/2022/21/1',
                                '/toc/tap/2018/15/4', '/toc/tap/2018/15/3', '/toc/tap/2018/15/2', '/toc/tap/2018/15/1',
                                '/toc/tap/2019/16/4', '/toc/tap/2019/16/3', '/toc/tap/2019/16/2', '/toc/tap/2019/16/1',
                                '/toc/tap/2020/17/4', '/toc/tap/2020/17/3', '/toc/tap/2020/17/2', '/toc/tap/2020/17/1',
                                '/toc/tap/2021/18/4', '/toc/tap/2021/18/3', '/toc/tap/2021/18/2', '/toc/tap/2021/18/1',
                                '/toc/tap/2022/19/1', '/toc/taslp/2018/26/12', '/toc/taslp/2018/26/11',
                                '/toc/taslp/2018/26/2', '/toc/taslp/2018/26/1', '/toc/taslp/2018/26/10',
                                '/toc/taslp/2018/26/9', '/toc/taslp/2018/26/8', '/toc/taslp/2018/26/7',
                                '/toc/taslp/2018/26/6', '/toc/taslp/2018/26/5', '/toc/taslp/2018/26/4',
                                '/toc/taslp/2018/26/3', '/toc/taslp/2019/27/12', '/toc/taslp/2019/27/11',
                                '/toc/taslp/2019/27/2', '/toc/taslp/2019/27/1', '/toc/taslp/2019/27/10',
                                '/toc/taslp/2019/27/9', '/toc/taslp/2019/27/8', '/toc/taslp/2019/27/7',
                                '/toc/taslp/2019/27/6', '/toc/taslp/2019/27/5', '/toc/taslp/2019/27/4',
                                '/toc/taslp/2019/27/3', '/toc/10.5555/taslp.2020.issue-28',
                                '/toc/10.5555/taslp.2021.issue-29', '/toc/10.5555/taslp.2022.issue-30',
                                '/toc/tcbb/2018/15/6', '/toc/tcbb/2018/15/5', '/toc/tcbb/2018/15/4',
                                '/toc/tcbb/2018/15/3', '/toc/tcbb/2018/15/2', '/toc/tcbb/2018/15/1',
                                '/toc/tcbb/2019/16/6', '/toc/tcbb/2019/16/5', '/toc/tcbb/2019/16/4',
                                '/toc/tcbb/2019/16/3', '/toc/tcbb/2019/16/2', '/toc/tcbb/2019/16/1',
                                '/toc/tcbb/2020/17/6', '/toc/tcbb/2020/17/5', '/toc/tcbb/2020/17/4',
                                '/toc/tcbb/2020/17/3', '/toc/tcbb/2020/17/2', '/toc/tcbb/2020/17/1',
                                '/toc/tcbb/2021/18/6', '/toc/tcbb/2021/18/5', '/toc/tcbb/2021/18/4',
                                '/toc/tcbb/2021/18/3', '/toc/tcbb/2021/18/2', '/toc/tcbb/2021/18/1',
                                '/toc/tcps/2018/2/4', '/toc/tcps/2018/2/3', '/toc/tcps/2018/2/2', '/toc/tcps/2018/2/1',
                                '/toc/tcps/2019/3/4', '/toc/tcps/2019/3/3', '/toc/tcps/2019/3/2', '/toc/tcps/2019/3/1',
                                '/toc/tcps/2020/4/4', '/toc/tcps/2020/4/3', '/toc/tcps/2020/4/2', '/toc/tcps/2020/4/1',
                                '/toc/tcps/2021/5/4', '/toc/tcps/2021/5/3', '/toc/tcps/2021/5/2', '/toc/tcps/2021/5/1',
                                '/toc/tcps/2022/6/2', '/toc/tcps/2022/6/1', '/toc/tds/2020/1/4', '/toc/tds/2020/1/3',
                                '/toc/tds/2020/1/2', '/toc/tds/2020/1/1', '/toc/tds/2021/2/4', '/toc/tds/2021/2/3',
                                '/toc/tds/2021/2/2', '/toc/tds/2021/2/1', '/toc/teac/2018/6/3-4', '/toc/teac/2018/6/2',
                                '/toc/teac/2018/6/1', '/toc/teac/2019/7/4', '/toc/teac/2019/7/3', '/toc/teac/2019/7/2',
                                '/toc/teac/2019/7/1', '/toc/teac/2019/7/2', '/toc/teac/2020/8/4', '/toc/teac/2020/8/3',
                                '/toc/teac/2020/8/2', '/toc/teac/2020/8/1', '/toc/teac/2021/9/4', '/toc/teac/2021/9/3',
                                '/toc/teac/2021/9/2', '/toc/teac/2021/9/1', '/toc/teac/2022/10/1',
                                '/toc/tecs/2018/17/6', '/toc/tecs/2018/17/5', '/toc/tecs/2018/17/4',
                                '/toc/tecs/2018/17/3', '/toc/tecs/2018/17/2', '/toc/tecs/2018/17/1',
                                '/toc/tecs/2019/18/6', '/toc/tecs/2019/18/5s', '/toc/tecs/2019/18/5',
                                '/toc/tecs/2019/18/4', '/toc/tecs/2019/18/3', '/toc/tecs/2019/18/2',
                                '/toc/tecs/2019/18/1', '/toc/tecs/2020/19/6', '/toc/tecs/2020/19/5',
                                '/toc/tecs/2020/19/4', '/toc/tecs/2020/19/3', '/toc/tecs/2020/19/2',
                                '/toc/tecs/2020/19/1', '/toc/tecs/2021/20/6', '/toc/tecs/2021/20/5',
                                '/toc/tecs/2021/20/4', '/toc/tecs/2021/20/3', '/toc/tecs/2021/20/2',
                                '/toc/tecs/2021/20/1', '/toc/tecs/2022/21/2', '/toc/tecs/2022/21/1',
                                '/toc/telo/2021/1/4', '/toc/telo/2021/1/3', '/toc/telo/2021/1/2', '/toc/telo/2021/1/1',
                                '/toc/telo/2022/2/1', '/toc/thri/2018/7/3', '/toc/thri/2018/7/2', '/toc/thri/2018/7/1',
                                '/toc/thri/2019/8/4', '/toc/thri/2019/8/3', '/toc/thri/2019/8/2', '/toc/thri/2019/8/1',
                                '/toc/thri/2020/9/4', '/toc/thri/2020/9/3', '/toc/thri/2020/9/2', '/toc/thri/2020/9/1',
                                '/toc/thri/2021/10/4', '/toc/thri/2021/10/3', '/toc/thri/2021/10/2',
                                '/toc/thri/2021/10/1', '/toc/thri/2022/11/2', '/toc/thri/2022/11/1',
                                '/toc/tiis/2018/8/4', '/toc/tiis/2018/8/3', '/toc/tiis/2018/8/2', '/toc/tiis/2018/8/1',
                                '/toc/tiis/2019/9/4', '/toc/tiis/2019/9/2-3', '/toc/tiis/2019/9/1',
                                '/toc/tiis/2020/10/4', '/toc/tiis/2020/10/3', '/toc/tiis/2020/10/2',
                                '/toc/tiis/2020/10/1', '/toc/tiis/2021/11/3-4', '/toc/tiis/2021/11/2',
                                '/toc/tiis/2021/11/1', '/toc/tiis/2022/12/1', '/toc/tiot/2020/1/4',
                                '/toc/tiot/2020/1/3', '/toc/tiot/2020/1/2', '/toc/tiot/2020/1/1', '/toc/tiot/2021/2/4',
                                '/toc/tiot/2021/2/3', '/toc/tiot/2021/2/2', '/toc/tiot/2021/2/1', '/toc/tiot/2022/3/3',
                                '/toc/tiot/2022/3/2', '/toc/tiot/2022/3/1', '/toc/tist/2018/9/6', '/toc/tist/2018/9/5',
                                '/toc/tist/2018/9/4', '/toc/tist/2018/9/3', '/toc/tist/2018/9/2', '/toc/tist/2018/9/1',
                                '/toc/tist/2019/10/6', '/toc/tist/2019/10/5', '/toc/tist/2019/10/4',
                                '/toc/tist/2019/10/3', '/toc/tist/2019/10/2', '/toc/tist/2019/10/1',
                                '/toc/tist/2020/11/6', '/toc/tist/2020/11/5', '/toc/tist/2020/11/4',
                                '/toc/tist/2020/11/3', '/toc/tist/2020/11/2', '/toc/tist/2020/11/1',
                                '/toc/tist/2021/12/6', '/toc/tist/2021/12/5', '/toc/tist/2021/12/4',
                                '/toc/tist/2021/12/3', '/toc/tist/2021/12/2', '/toc/tist/2021/12/1',
                                '/toc/tist/2022/13/4', '/toc/tist/2022/13/3', '/toc/tist/2022/13/2',
                                '/toc/tist/2022/13/1', '/toc/tkdd/2018/12/6', '/toc/tkdd/2018/12/5']


@wait(6)
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


@wait(6)
def click_wrapper(element):
    element.click()


def collect_all_citations():
    publications = get_documents_from_firestore(JOURNAL_COLLECTION)
    for p in publications:
        journal_publication_data = p.get().to_dict()
        journal = journal_publication_data.get("journal")
        link = journal_publication_data.get("link")
        if link not in already_done_journals_issues:
            try:
                collect_citations_for_journal_issue(journal, link)
                already_done_journals_issues.append(link)
                print(f'[{timestamp()}]done with: {already_done_journals_issues}')
                print_and_pickle_all_already_scrapped_entries()
            except NoSuchElementException as e:
                print(e)
                logger.warning(f"restarting after failure: {e}")
                print("restarting...")
                collect_all_citations()

        else:
            print(f'already done with {link}')


def print_and_pickle_all_already_scrapped_entries():
    # print(*already_done_journals_issues, sep=' ')
    pickle.dump(already_done_journals_issues, open("save.p", "wb"))


@wait(30)
def collect_citations_for_journal_issue(journal: str, journal_publication_link: str):
    parser = create_parser()

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    url = f'{HOST_URL}{journal_publication_link}'
    print(url)
    driver.get(url)  # url associated with button click

    click_wrapper(driver.find_element(By.TAG_NAME, "body"))
    sleep(5)

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
        # logger.info(bibtext_raw_str)
        # bibtext_raw_logger.info(bibtext_raw_str)

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
