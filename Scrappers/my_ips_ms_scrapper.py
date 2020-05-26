# http://allselenium.info/python-selenium-all-mouse-actions-using-actionchains/
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import time
global driver
global actions
global my_ips_sites_list
# Print data for testing


# EQESBMB9VC9CQRUJCDFIKGM

def extract_all_sites(number_of_pages):
    # actions.move_to_element(driver.find_element_by_xpath("// *[ @ id = 'sites_tbl'] / thead[1] / tr[1] / th[7]")).perform()

    for page_number in range(1, number_of_pages):
        print("#" + str(page_number))
        # item = extract_item()
        # if item:
        #     sheet.add_product_to_sheet(item)
        next_page = get_next_page_location(page_number+1)
        if next_page:
            actions.move_to_element(next_page).perform()
            time.sleep(2)
            actions.click(next_page).perform()
            time.sleep(3)
            check_if_robot()
        else:
            print("End of pages")


def check_if_robot():
    captcha_submit = get_im_not_robot_button()
    if captcha_submit:
        actions.move_to_element(captcha_submit).perform()
        time.sleep(2)
        actions.click(captcha_submit)
        time.sleep(3)
    else:
        print("No check_if_robot found")


def extract_item():
    try:
        item = {
            'title': driver.find_element_by_class_name('product_title').text,
        }
        return item
    except Exception as e:
        print("Cant extract_item item", e)


def get_next_page_location(page_number):
    try:
        return driver.find_element_by_xpath(f"//*[@id='tabs-1']/table[2]/tbody[1]/tr[1]/td[1]/span[1]/span[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[1]/a[{page_number}]")
    except Exception as e:
        print("Cant get_next_page_location", e)


def get_im_not_robot_button():
    try:
        return driver.find_element_by_id("captcha_submit")
    except Exception as e:
        print("Cant get_im_not_robot_button", e)


class MyIpsMsScrapper:

    LINK = "https://myip.ms/browse/sites/1/host/myshopify.com/host_A/1"

    def __init__(self, _sheet):
        global my_ips_sites_list
        global driver
        global actions
        sheet = _sheet
        # Don't show the Chrome browser
        useragent = UserAgent().random
        print(useragent)
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        options.add_argument(f'user-agent={useragent}')
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=options)
        driver.get(self.LINK)
        time.sleep(3)

        actions = ActionChains(driver)

        #
        #
        # driver.find_element_by_id("user_login").send_keys(username)
        # driver.find_element_by_id("user_pass").send_keys(password)
        #
        # driver.find_element_by_id("wp-submit").click()
        #
        # time.sleep(4)
        #
        # driver.find_element_by_xpath(self.All_PRODUCTS).click()
        #
        # time.sleep(4)
        #
        # driver.find_element_by_xpath(self.FIRST_ITEM).click()
        #
        # time.sleep(5)

        extract_all_sites(number_of_pages=3)

        # Get the position based on results
