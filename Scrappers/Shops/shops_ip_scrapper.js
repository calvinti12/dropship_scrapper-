
const userAgent = require('user-agents');
const puppeteer = require('puppeteer');
const captcha = require("async-captcha");

const APIKEY = '46bb6e3142c2823a5ea4e0a2a7bc1357';

let headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Origin': 'https://myip.ms',
    'Referer': 'https://myip.ms/browse/sites/1/own/376714/sort/6/asc/1#sites_tbl_top'
};

let browser, page

const CAPTCHA_SUBMIT = '.btn';
const CAPTCHA_IMAGE = "//img[starts-with(@src,'/captcha')]";
const ODD_CELL = '.odd';
const EVEN_CELL = '.even';

const SEC = 1000;

const captcha_options = {
    case: false,
    minLength: 4,
    maxLength: 8
};

const PUPPETEER_OPTIONS = {
    args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--ignore-certificate-errors',
        '--lang=ja,en-US;q=0.9,en;q=0.8',
    ],
    headless: true,
    devtools: false,
    slowMo:10,
    ignoreHTTPSErrors: true,
    ignoreDefaultArgs: ['--disable-extensions']
};

const defaultViewport = {
    deviceScaleFactor: 1,
    hasTouch: false,
    height: 1024,
    isLandscape: false,
    isMobile: false,
    width: 1280
};

const anticaptcha = new captcha(APIKEY, 2, 5);

const open_connection = async () => {
    browser = await puppeteer.launch(PUPPETEER_OPTIONS);
    page = await browser.newPage();
    await page.setViewport(defaultViewport);
    await page.setUserAgent(userAgent.toString());
    await page.setExtraHTTPHeaders(headers);

    page.on('error', async err => {
        console.log("Error page - " + err );
        await close_connection()
        await open_connection()
    })
};

const close_connection = async () => {
    page && (await page.close());
    browser && (await browser.close());
};

const format_page_id = (page) =>{
    return `https://myip.ms/browse/sites/${page}/own/376714/sort/6/asc/1#a`
};


const get_page = async (page_number, number_of_pages, attempts) => {
    await open_connection();
    let pages_data = []
    for(let i=page_number ; i<=page_number + number_of_pages;i++) {
        const raw_data = await page_fetch_retry(page, i, attempts);
        pages_data = pages_data.concat(raw_data)
    }
    await close_connection();
    return pages_data
};


const page_fetch_retry = async (page, page_number, attempt_left) => {
    try {
        let page_data = await scrape_page(page, page_number);
        if(!page_data) {
            throw new Error("page_id null");
        }
        let sites =  await extract_site_data(page_data);
        console.log(`Extracted ${sites.length} sites from page number ${page_number} at the ${6 - attempt_left} attempt`);
        return sites;
    } catch (error) {
        if (attempt_left <= 1) {
            console.log("Error getting page_fetch_retry - " + error.message + " page_number -" +page_number);
            return []
        }
        else {
            await sleep(2000);
            return await page_fetch_retry(page, page_number, attempt_left - 1);
        }
    }
};

const extract_site_data = async (sites) => {
    sites = await sites.map(el=>{
        let item = el.split('\t');
        return {link:item[1],ranking:item[6].replace( /^\D+/g, '').replace(',', '')}
    });
    return sites;
};

const scrape_page = async (page, page_number) => {
    try {
        if (page && !page.isClosed()) {
            await page.goto(format_page_id(page_number), { timeout: SEC*10, waitUntil: 'domcontentloaded' });
            let is_table_exists = await isElementVisible(page, ODD_CELL);
            let is_captcha_solved = false
            if (!is_table_exists)
                is_captcha_solved = await solve_captcha(page);
            if (is_captcha_solved || is_table_exists) {
                is_table_exists = await isElementVisible(page, ODD_CELL)
                if (is_table_exists) {
                    return await extract_cells(page)
                } else {
                    console.log("Error no table exists after solving captcha- " + page_number);
                }
            } else {
                console.log("Error solving captcha for page - " + page_number);
            }
        }
        else {
            await sleep(5000);
        }
    } catch (err) {
        console.log("Error scrape_page - " + err.message )
    }
    return null
};

const extract_cells = async (page) => {
    let odd_cells = await page.$$eval(ODD_CELL, els => els.map(el => el.innerText).filter(el => el.length > 2));
    let even_cells = await page.$$eval(EVEN_CELL, els => els.map(el => el.innerText).filter(el => el.length > 2));
    return odd_cells.concat(even_cells);
}

const solve_captcha = async (page) => {
    try {
        console.time('all solve captcha time:')
        let is_humen_button_exists = await isElementVisible(page, CAPTCHA_SUBMIT);
        let is_captcha_image_exists = await isXPatchElementVisible(page, CAPTCHA_IMAGE);
        while (is_humen_button_exists && !is_captcha_image_exists) {
            await page
                .click(CAPTCHA_SUBMIT)
                .catch(() => {});
            is_humen_button_exists = await isElementVisible(page, CAPTCHA_SUBMIT);
            is_captcha_image_exists = await isXPatchElementVisible(page, CAPTCHA_IMAGE);
        }
        const elementHandler = await page.$x(CAPTCHA_IMAGE);
        // base64String contains the captcha image's base64 encoded version
        const base64String = await elementHandler[0].screenshot({ encoding: "base64" });
        console.time('only result captcha time:')
        const captchaCode = await anticaptcha.getResult(base64String,captcha_options);
        console.timeEnd('only result captcha time:')
        if(captchaCode) {
            console.log('we found a captcha Code - ' + captchaCode);
            await page.type('input[name=p_captcha_response]', captchaCode, {delay: 20})
            await page.click('[type="submit"]')
            await sleep(3000);
            console.timeEnd('all solve captcha time:')
            return true;
        }
        else {
            console.log('we didnt found a captcha Code');
        }
    }
    catch (e) {
        console.log('no recaptcha found in page, error' + e);
    }
    console.timeEnd('all solve captcha time:')
    return false;
};

const isElementVisible = async (page, selector) => {
    let visible = true;
    await page
        .waitFor(selector, { visible: true, timeout: 2000 })
        .catch(() => {
            visible = false;
        });
    return visible;
};

const isXPatchElementVisible = async (page, selector) => {
    let visible = true;
    await page
        .waitForXPath(selector, { visible: true, timeout: 2000 })
        .catch(() => {
            visible = false;
        });
    return visible;
};


exports.scraping_sites = async (req, res) => {
    let page = req.query.start_page || 1;
    let number_of_pages = req.query.number_of_pages || 10;
    let attempts = req.query.attempts || 4;
    let page_data = await get_page(page, number_of_pages, attempts);
    return res.status(200).json(page_data);
};

const test = async (page, number_of_pages, attempts) => {
    console.time('total msip time:')
    let page_data = await get_page(page,number_of_pages, attempts);
    console.timeEnd('total msip time:')
    console.log(page_data);
};

const sleep = async (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms))
};