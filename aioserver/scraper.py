import asyncio
import json
import logging
import time
from pathlib import Path

import aiohttp
from curl_cffi import requests
from tqdm.asyncio import tqdm_asyncio

from aioserver.filter import MainFilter
from aioserver.item_json import json_fetched
from config import COUCHDB_URL, DB_NAME, headers

# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )


class MainScrap:
    #
    def __init__(self) -> None:
        self.sessio = aiohttp.ClientSession()
        self.middleware = None
        self.cookie = {}
        self.header = None
        pass

    def browse(self):
        pass

    def feed(self):
        pass

    def saitco(self):
        return save_item_couch(self.sessio, self.cookie)


async def save_item_couch(session: aiohttp.ClientSession, item: dict):
    """
    Saving every json items scrapped in an async fashion into a NoSQL using
    async requests from aiohttp instead of the proper couchdb library.
    A queue worker must be use in order to update element of json,
    the _rev ...
    """

    url = f"{COUCHDB_URL}/{DB_NAME}/{item['_id']}"
    header = {"Content-Type": "application/json"}

    async with session.put(url, data=json.dumps(item), headers=header) as resp:
        if resp.status == 201:
            # logging.info(f"Doc {item['_id']} insert")
            return item

        elif resp.status == 409:
            # logging.info(f"Doc {item['_id']} already exist")
            return

        # else:
        #    text = await resp.text()
        #    raise Exception(f"Erreur {resp.status}: {text}")


async def fetch_one(session: requests.AsyncSession, url: str):
    # download one json from one url, asynchronously
    try:
        r = await session.get(url)
        if r.status_code == [400, 401, 403, 404, 406]:
            logging.info(f"Error of type {r.status_code} on {url}")
            return
        else:
            return r.json()
    except requests.RequestsError as e:
        print(f"Error on session of type {e}")


async def fetch_image(session: aiohttp.ClientSession, item, sem):
    """
    Fetch image only if 'save_item_couch' return the item or not
    hence leading to no over-scraping image we have already
    """
    item_id = item.get("_id")
    image_url = item.get("photo")

    img_filename = Path("images") / f"{item_id}.jpg"

    try:
        async with sem:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(img_filename, "wb") as img_file:
                        img_file.write(await response.read())  # download image
                else:
                    logging.error(f"HTTP error {response.status} for {image_url}")
    except aiohttp.ClientConnectionError as e:
        logging.error(f"Error during download of {image_url}: {e}")


async def main(urls):
    #
    response = requests.get("https://www.vinted.com", headers=headers)
    cookies = dict(response.cookies.items())
    sem = asyncio.Semaphore(48)

    # FIRST json are requested with async-curl_cffi, more robust thanks to the
    # fingerprint added because the so-called json are hard to access
    async with requests.AsyncSession(headers=headers, cookies=cookies) as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    jsons = tuple(map(json_fetched, results))

    # SECOND async-aio, still more suitable for async task is called for
    # images requests, and images/items saving
    async with aiohttp.ClientSession(cookies=cookies) as aiosession:
        save_tasks = [
            save_item_couch(aiosession, item) for json in jsons for item in json
        ]

        images_json = await tqdm_asyncio.gather(*save_tasks)

        # transform and save into couch before images because it could lead to fail
        # because fetch image depend on these change (change of key: value pair)

        image_tasks = [
            fetch_image(aiosession, item, sem) for item in images_json if item
        ]
        item_saved = await tqdm_asyncio.gather(*image_tasks)

        logging.info(f"{len(item_saved)} new items saved.")


if __name__ == "__main__":
    pass
