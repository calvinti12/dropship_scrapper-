from selenium import webdriver
import time
import random
global driver
global sites_worksheet
# Print data for testing


def extract_all_items():

    item = extract_item()
    if item:
        sites_worksheet.add_product_to_sheet(item)

    driver.find_element_by_class_name('next')


def extract_item():
    try:
        item = {
            'title': driver.find_element_by_class_name('product_title').text,
            'SELLING PRICE': driver.find_element_by_id('productSellingPrice').text,
            'PRODUCT COST': driver.find_element_by_id('productCost').text,
            'PROFIT MARGIN': driver.find_element_by_id('productProductMargin').text,
            'rabbit_link': driver.current_url,
            'Alibaba_link': get_alibaba_link(),
            'Video_link': get_video_link()
        }
        return item
    except Exception as e:
        print("Cant extract_item item", e)


def get_alibaba_link():
    try:
        return driver.find_element_by_partial_link_text('Alibaba').get_attribute("href")
    except Exception as e:
        print("Cant get_alibaba_link", e)
        return "-"


def get_video_link():
    try:
        return driver.find_element_by_partial_link_text('Download Video').get_attribute("href")
    except Exception as e:
        print("Cant get_video_link", e)
        return "-"


class DropShipRabbitScrapper:

    LINK = "https://dropshiprabbit.com/wp-login.php?action=login"

    # Where should selenium click to go to the minute tab.
    MINUTE_XPATH = "//*[@id='technicals-root']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]"

    All_PRODUCTS = "//*[@id='Content']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/p[2]/a[1]"

    FIRST_ITEM = "//*[@id='Content']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/ul[1]/li[1]/div[2]/h4[1]/a[1]"

    def __init__(self, username, password, _sheet):
        global sites_worksheet
        global driver
        sheet = _sheet
        # Don't show the Chrome browser
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")

        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=options)
        driver.get(self.LINK)
        time.sleep(7)

        driver.find_element_by_id("user_login").send_keys(username)
        driver.find_element_by_id("user_pass").send_keys(password)

        driver.find_element_by_id("wp-submit").click()

        time.sleep(4)

        driver.find_element_by_xpath(self.All_PRODUCTS).click()

        time.sleep(4)

        driver.find_element_by_xpath(self.FIRST_ITEM).click()

        time.sleep(5)

        extract_all_items()

        # Get the position based on results
