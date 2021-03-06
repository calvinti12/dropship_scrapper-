const puppeteer = require('puppeteer');

const NUMBER_OF_LIKES = '._8wi7';
const PAGE_CREATED = '._3-99';
const ACTIVE_ADS = '._7gn2';
const LATEST_RUNNING_AD = '._7jwu';

const SEE_MORE = '._5u7u';

const FACEBOOK_ADS_LIBRARY = 'https://www.facebook.com/ads/library/?';
const headers = {
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
};
const SEC = 1000;

const PUPPETEER_OPTIONS = {
    headless: true,
    args: ['--no-sandbox'],
    ignoreDefaultArgs: ['--disable-extensions']
};
let init_ads = {
    'link':'',
    'page_id':'',
    'active_ads': 0,
    'latest_running_ad': '01/01/1971',
    'likes': 0,
    'instagram_followers': 0,
    'niche': '',
    'page_created': new Date().toUTCString(),
    'updated': new Date().toUTCString(),
    'ok':false,
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
    };
    return  FACEBOOK_ADS_LIBRARY + new URLSearchParams(qs).toString();
};


const get_ads = async (facebook_page_url,attempts_left) => {
    let { browser, page } = await openConnection();
    init_ads['link'] = facebook_page_url;
    let page_id =  await page_id_fetch_retry(page, facebook_page_url, attempts_left);
    if(page_id) {
        init_ads['page_id'] = page_id;
        init_ads = await ads_fetch_retry(page, init_ads, attempts_left);
    }
    await closeConnection(page, browser);
    return init_ads
};

const scrape_ads = async (page, ads) => {
    try {
        await page.goto(format_page_id(ads['page_id']), { timeout: SEC*20 });
        await page.waitFor(NUMBER_OF_LIKES, { timeout: SEC*5 });
        let likes_followers =await page.$$eval(NUMBER_OF_LIKES, els=> els.map(el => el.innerText));
        ads['likes'] = likes_followers[0].split('\n')[0].replace(',', '');
        ads['niche']  = likes_followers[0].split('\n')[likes_followers[0].split('\n').length-1];
        if(likes_followers.length >1)
            ads['instagram_followers'] = likes_followers[1].split(' ')[0].replace(',', '');
        ads['active_ads'] = await page.$eval(ACTIVE_ADS, el=>  el.innerText.replace(/\D/g, ""));
        let page_created = await page.$$eval(PAGE_CREATED, els=> els.map(el => el.innerText).filter(date =>(new Date(date) !== "Invalid Date") && !isNaN(new Date(date))));
        ads['page_created'] = page_created[0];
        if (Number(ads['active_ads'])>0)
        {
            await page.waitFor(LATEST_RUNNING_AD, { timeout: SEC*5 });
            let ad_divs =await page.$$eval(LATEST_RUNNING_AD, ads=>ads.map(ad => ad.innerText));
            ads['latest_running_ad'] = await parse_date(ad_divs[0])
        }
        ads['ok'] = true;
        return ads
    } catch (err) {
        console.log("Error getting ads - " + err.message + " pageId -" + ads['page_id']);
        return ads
    }
};

const scrape_page_id = async (page, facebook_page_url) => {
    try {
        await page.goto(facebook_page_url, { timeout: SEC*20 });
        await page.waitFor(SEE_MORE, { timeout: SEC*3 });
        const hrefs = await page.$$eval('a', as =>
            as.map(a => a.href)
                .filter(a =>(a.includes('photos')))
                .map(a => a.split('/photos')[0])
                .map(a => a.split('https://www.facebook.com/')[1])
                .filter(a => !isNaN(a))
        );

        let links = [...new Set(hrefs)];
        if (links.length > 1)
            console.log("Found more links then 1 - " + links + " facebook_page_url -" + facebook_page_url);
        return links[0];
    } catch (err) {
        console.log("Error getting scrape_page_id - " + err.message + " facebook_page_url -" + facebook_page_url);
        return null
    }
};

const ads_fetch_retry = async (page, ads, attempt) => {
    try {
        ads = await scrape_ads(page, ads);
        if(!ads.ok) {
            throw new Error("ads not ok");
        }
        return ads;
    } catch (error) {
        if (attempt <= 1) {
            console.log("Error getting ads - " + error.message + " pageId -" + ads['page_id']);
            return await scrape_ads(page, ads);
        }
        else {
            await sleep(1000);
            return await ads_fetch_retry(page, ads, attempt - 1);
        }
    }
};

const page_id_fetch_retry = async (page, facebook_page_url, attempt) => {
    try {
        let page_id = await scrape_page_id(page, facebook_page_url);
        if(!page_id) {
            throw new Error("page_id null");
        }
        return page_id;
    } catch (error) {
        if (attempt <= 1) {
            console.log("Error getting page_id_fetch_retry - " + error.message + " facebook_page_url -" +facebook_page_url);
            return null
        }
        else {
            await sleep(1000);
            return await page_id_fetch_retry(page, facebook_page_url, attempt - 1);
        }
    }
};

const parse_date = async (date_string) => {
    return date_string.toLowerCase().replace('started running on ', '')
};

exports.scraping_ads = async (req, res) => {
    let facebook_page_url = req.query.link;
    let attempts = req.query.attempts || 4;
    let ads = await get_ads(facebook_page_url,attempts);
    return res.status(200).json(ads);
};


const test = async (facebook_page_url) => {
    let ads = await get_ads(facebook_page_url,5);
    console.log(ads);
};

const sleep = async (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms))
};