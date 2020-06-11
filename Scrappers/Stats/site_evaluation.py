from selenium import webdriver
import time
import random
from Database.atlas import evaluate_site

global driver

HTML_TEXT = "<p>Site:TEST</p>" \
            "<p>Number of products: {{number_of_products}}</p>" \
            "<p>Last updated: {{last_product_updated}}</p>" \
            "<select name='option' width='300px'>" \
            "< option value = 'TEST' > TEST < / option >" \
            "</select>"


class SiteEvaluation:

    FIRST_ITEM = "//*[@id='Content']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[1]/div[2]/h4[1]/a[1]"

    def __init__(self):
        global driver
        # Don't show the Chrome browser
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")

        driver = webdriver.Chrome(executable_path=r"Scrappers/chromedriver.exe", chrome_options=options)

    def get_site(self, link):
        driver.get(link)
        time.sleep(7)

        elm = driver.find_element_by_id("shopify-section-header")
        driver.execute_script("arguments[0].innerHTML =" + HTML_TEXT, elm)

    def save_evaluation(self, link, is_dropshipper, niche, main_product, is_branded_products):
        evaluate_site(link, is_dropshipper, niche, main_product, is_branded_products)