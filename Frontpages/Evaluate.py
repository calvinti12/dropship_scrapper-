from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By

import time

driver = webdriver.Firefox()

driver.maximize_window()

location = "file://<Specify Path to IFrame.HTML>"

driver.get(location)

########Section-1

# get the list of iframes present on the web page using tag "iframe"

seq = driver.find_elements_by_tag_name('iframe')

print("No of frames present in the web page are: ", len(seq))

#switching between the iframes based on index

for index in range(len(seq)):

    driver.switch_to_default_content()

    iframe = driver.find_elements_by_tag_name('iframe')[index]

    driver.switch_to.frame(iframe)

    driver.implicitly_wait(30)

    #highlight the contents of the selected iframe

    driver.find_element_by_tag_name('a').send_keys(Keys.CONTROL, 'a')

    time.sleep(2)

    # undo the selection within the iframe

    driver.find_element_by_tag_name('p').click()

    driver.implicitly_wait(30)

driver.switch_to.default_content()

########Section-2

#switch to a specific iframe (First frame) using Id as locator

iframe = driver.find_element_by_id('FR1')

driver.switch_to.frame(iframe)

time.sleep(2)

driver.find_element_by_id('s').send_keys("Selected")

driver.switch_to.default_content()


########Section-3

#switch to a specific iframe (Second frame) using name as locator

iframe = driver.find_element_by_name('frame2')

driver.switch_to.frame(iframe)

time.sleep(2)

driver.find_element_by_tag_name('a').send_keys(Keys.CONTROL, 'a')