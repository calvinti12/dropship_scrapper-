from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import statistics
import re
import time
import random
global driver
global actions
global my_ips_sites_worksheet


def send_keys_decimal(text, element):
    string_items = text.split('.')
    element.send_keys(string_items[0])
    string_items.pop(0)
    while string_items:
        element.send_keys(Keys.DECIMAL)
        element.send_keys(string_items[0])
        string_items.pop(0)


class NicheScrapper:

    LINK = "https://nichescraper.com/login.php"

    # Where should selenium click to go to the minute tab.
    MINUTE_XPATH = "//*[@id='technicals-root']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]"

    STORE_ANALYSIS = "//*[@id='wrap']/div[1]/a[5]/span[1]"

    SEARCH_BAR = "//*[@id='store-search-bar']"
    SEARCH_BUTTON = "//*[@id='store-search-button']"

    def __init__(self, username, password):
        global driver
        global actions
        # Don't show the Chrome browser
        options = webdriver.ChromeOptions()
        options.add_argument('no-sandbox')
        options.add_argument("headless")

        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=options)
        actions = ActionChains(driver)
        driver.get(self.LINK)
        send_keys_decimal(username, driver.find_element_by_id("email-input"))
        send_keys_decimal(password, driver.find_element_by_id("password"))
        driver.find_element_by_id("submit-button").click()
        time.sleep(3)

    def analysis_store(self, site):
        driver.get('https://nichescraper.com/analysis/?site=' + site.link)
        number_of_best_sellers_products = 0
        try:
            element_present = ec.presence_of_element_located((By.CLASS_NAME, 'product-col'))
            WebDriverWait(driver, 10).until(element_present)
            print("Page is ready!")
            time.sleep(2)
            # body = driver.find_element_by_css_selector('body')
            # body.send_keys(Keys.PAGE_DOWN)
            # time.sleep(3)
            # body = driver.find_element_by_css_selector('body')
            # body.send_keys(Keys.PAGE_DOWN)
            # time.sleep(3)

            best_sellers = driver.find_elements_by_class_name('b-product-results')
            products = best_sellers[0].text.split('\n')
            prices = []
            product_avg = 0
            i = 1
            while i <= len(products) and len(products) > 1:
                price = float(re.sub("[^\d\.]", "", products[i]))
                product_avg += price
                prices.append(price)
                i += 2

            site.set_products(len(prices), product_avg/len(prices), statistics.median(prices))
        except Exception as e:
            print(f"Error analysis_store , site {site.link}", e)

    def close_driver(self):
        driver.close()
        driver.quit()



