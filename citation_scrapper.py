from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from tkinter import Tk

from selenium.webdriver.common.by import By

from util import sleep

HOST_URL = "https://dl.acm.org/"


@sleep(5)
def click_element(element, driver):
    webdriver.ActionChains(driver).move_to_element(element).click(element).perform()

@sleep(5)
def f():
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.get(f'{HOST_URL}toc/jacm/2021/68/4')  # url associated with button click
    elements = driver.find_elements(By.XPATH, "//li/a[@class='btn--icon simple-tooltip__block--b'][@aria-label='Export Citation']")

    print(elements)

    for element in elements:
        print(element)
        click_element(element, driver)
        cpy_to_clipboard_btn = driver.find_element(By.XPATH, "//a[@class='copy__btn'][@title='Copy citation'][@role='menuitem']")
        print(cpy_to_clipboard_btn)
        click_element(cpy_to_clipboard_btn, driver)
        clipboard = Tk().clipboard_get()
        print(clipboard)


    # button = driver.find_element(by=By.TAG_NAME, value="a")).get_attribute("value")

# export citation btn
# <a>
# class="btn--icon simple-tooltip__block--b"
# aria-label="Export Citation"

# copy btn
# <a href="javascript:void(0)" role="menuitem" title="Copy citation" class="copy__btn"><label class="visibility-hidden">Copy citation</label><i aria-hidden="true" class="icon-pages"></i><input type="hidden" id="doisLimitNumber" value="-1"></a>


if __name__ == '__main__':
    f()
