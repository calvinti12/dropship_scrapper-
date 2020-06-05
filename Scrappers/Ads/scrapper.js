const puppeteer = require('puppeteer');

const NUMBER_OF_LIKES = '._8wi7';
const PAGE_CREATED = '._3-99';
const ACTIVE_ADS = '._7gn2';
const LATEST_RUNNING_AD = '._7jwu';
const FACEBOOK_ADS_LIBRARY = 'https://www.facebook.com/ads/library/?'
const headers = {
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
}

const PUPPETEER_OPTIONS = {
    headless: true,
    args: ['--no-sandbox'],
    ignoreDefaultArgs: ['--disable-extensions']
};

const openConnection = async () => {
    const browser = await puppeteer.launch(PUPPETEER_OPTIONS);
    const page = await browser.newPage();
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    );
    await page.setExtraHTTPHeaders(headers);
    return { browser, page };
};


const closeConnection = async (page, browser) => {
    page && (await page.close());
    browser && (await browser.close());
};

const format_page_id = (page_id) =>{
    let qs = {
        'active_status': "all",
        'country': "ALL",
        'ad_type': "all",
        'impression_search_field': "has_impressions_lifetime",
        'view_all_page_id': page_id
    }
    return  FACEBOOK_ADS_LIBRARY + new URLSearchParams(qs).toString();
}

const get_ads = async (page_id) => {
    let ads = {
        'page_id':page_id,
        'active_ads': 0,
        'latest_running_ad': '01/01/1971',
        'likes': 0,
        'instagram_followers': 0,
        'niche': '',
        'page_created': new Date().toUTCString(),
        'updated': new Date().toUTCString()
    }
    let { browser, page } = await openConnection();
    try {
        await page.goto(format_page_id(page_id), { timeout: 50000 })
        await page.waitFor(NUMBER_OF_LIKES, { timeout: 3000 });
        let likes_followers =await page.$$eval(NUMBER_OF_LIKES, els=> els.map(el => el.innerText));
        ads['likes'] = likes_followers[0].split('\n')[0].replace(',', '')
        ads['niche']  = likes_followers[0].split('\n')[likes_followers[0].split('\n').length-1]
        if(likes_followers.length >1)
            ads['instagram_followers'] = likes_followers[1].split(' ')[0].replace(',', '')
        ads['active_ads'] = await page.$eval(ACTIVE_ADS, el=>  el.innerText.replace(/\D/g, ""));
        let page_created = await page.$$eval(PAGE_CREATED, els=> els.map(el => el.innerText).filter(date =>(new Date(date) !== "Invalid Date") && !isNaN(new Date(date))));
        ads['page_created'] = page_created[0]
        await page.waitFor(LATEST_RUNNING_AD, { timeout: 10000 });
        let ad_divs =await page.$$eval(LATEST_RUNNING_AD, ads=>ads.map(ad => ad.innerText))
        ads['latest_running_ad'] = await parse_date(ad_divs[0])
        return ads;
    } catch (err) {
        console.log("Error getting ads - " + err.message);
        return ads;
    } finally {
        await closeConnection(page, browser);
    }
};

const parse_date = async (date_string) => {
    return date_string.toLowerCase().replace('started running on ', '')
};

exports.scraping_ads = async (req, res) => {
    let page_id = req.query.link;
    let ads = await get_ads(page_id)
    return res.status(200).json(ads);
}

const test = async () => {
    let page_id = '540592139767475';
    let ads = await get_ads(page_id)
    console.log(ads);
};