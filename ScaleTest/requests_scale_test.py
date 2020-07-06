import asyncio
from aiohttp import ClientSession, ClientTimeout
from fake_useragent import UserAgent

url = "https://us-east4-dropshipscrapper.cloudfunctions.net/google_trends_api_1"

payload = 'hours_in_trend=48&max_workers=50&key_words=World%20Cup&key_words=Fortnite&key_words=Kim%20Kardashian'
headers = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
    'Connection': 'keep-alive',
    'User-Agent': '',
}


async def fetch(session):
    headers['User-Agent'] = UserAgent().random
    async with session.post(url, data=payload, headers=headers) as response:
        response_text = await response.text()
        print("res ", response_text)
        return response_text


async def bound_fetch(sem, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(session)


async def run(r):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i in range(r):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


def run_test(number):
    # make 10k requests per second ?? (not confident this is true)
    loop = asyncio.get_event_loop()

    future = asyncio.ensure_future(run(number))
    loop.run_until_complete(future)
