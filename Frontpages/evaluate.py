from flask import Flask, render_template
niche_list = ["Pets",
              "House improvements",
              "Security",
              "Beauty & pleasure",
              "Personal health",
              "Babies & Kids",
              "Fitness Workout",
              "Electronics & Gadgets",
              "Jewels & Watches"]


def fix_url(url):
    fixed_url = url.strip()
    if not fixed_url.startswith('http://') and \
            not fixed_url.startswith('https://'):
        fixed_url = 'https://' + fixed_url
    return fixed_url.rstrip('/')


class Evaluate:
    def __init__(self):
        pass

    def open_site(self, site):
        link = fix_url(site['link'])
        return render_template('template.html',
                               link=link,
                               data_link=site['link'],
                               number_of_products=str(site['number_of_product']),
                               last_product_updated=str(site['last_product_updated']),
                               first_product_published=str(site['first_product_published']),
                               niche_list=niche_list)

