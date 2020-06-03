from selenium import webdriver
from flask import Flask, render_template

driver = None

niche_list = ["Pets",
              "House improvements",
              "Security",
              "Beauty & pleasure",
              "Personal health",
              "Babies & Kids",
              "Fashion",
              "Fitness Workout",
              "Electronics & Gadgets",
              "Jewels & Watches"]


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
            not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url
    return fixed_url.rstrip('/')


def open_site(site):
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", chrome_options=options)

    link = fix_url(site['link'])
    driver.get(link)
    return render_template('template.html',
                           link=link,
                           data_link=site['link'],
                           number_of_products=str(site['number_of_product']),
                           last_product_updated=str(site['last_product_updated']).replace(' 00:00:00', '')[::-1],
                           first_product_published=str(site['first_product_published']).replace(' 00:00:00', '')[::-1],
                           niche_list=niche_list)


