import asyncio
import logging
import os
import random
from pathlib import Path
from time import time

import aiohttp
import requests as rq
from aiohttp import CookieJar
from curl_cffi import requests
from requests.api import head

from config import REDIS_PORT, headers, id_user
from src.filter import Filter
from src.item_json import json_file, save_item_couch

# class Scraper(Filter):
#     def __init__(self, id: int) -> None:
#         super().__init__(id)
#         self.db = datab


async def fetch_json(session, urls):
    # fetch json in async
    try:
        async with session.get(urls) as response:
            if response.status == 200:
                print("[INFO] json fetched")
                return await response.json()
            elif response.status in [401, 403]:
                REDIS_PORT.delete("access_token_web")
                return "COOKIE_INVALID"

    except aiohttp.ClientResponseError as e:
        logging.error(f"Either the cookie is invalid or the IP is blocked: {e}")


async def fetch_image(session, item, sem):
    # download one image, asynchronously
    item_id = item.get("_id")
    image_url = item.get("photo")
    if not item_id or not image_url:
        logging.warning(f"Item avec ID {item_id} est manquant ou sans photo, ignoré.")
        return

    img_filename = Path("images") / f"{item_id}.jpg"

    if os.path.exists(img_filename):
        logging.Logger(
            f"L'image pour l'ID {item_id} existe déjà, saut du téléchargement."
        )
        return

    try:
        async with sem:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(img_filename, "wb") as img_file:
                        img_file.write(await response.read())  # Télécharger l’image
                    print(f"Image {item_id} téléchargée avec succès !")
                else:
                    logging.error(
                        f"Erreur HTTP {response.status} pour l'image {image_url}"
                    )
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement de l'image {image_url}: {e}")


async def alt_main(urls, cooks):
    # damn = random.randint(33, 66)
    sem = asyncio.Semaphore(1000)
    jar = CookieJar()
    for k, v in cooks.items():
        jar.update_cookies({k: v})

    # cookies = {"access_token_web": str(cookie_tes(r, headers=headers))}
    # cookies_dif = {"access_token_web": non}
    async with aiohttp.ClientSession(headers=headers, cookie_jar=jar) as session:
        # lauch the process with hopefully the right cookie
        json_tasks = [fetch_json(session, url) for url in urls]
        json_results = await asyncio.gather(*json_tasks)
        print(json_results[0])
        jsons = tuple(map(json_file, json_results))

        save_tasks = [save_item_couch(session, item) for json in jsons for item in json]
        await asyncio.gather(*save_tasks)
        # transform and save into couch before images because it could lead to fail
        # because fetch image depend on these change (change of key: value pair)

        image_tasks = [
            fetch_image(session, item, sem) for json in jsons for item in json
        ]
        await asyncio.gather(*image_tasks)


dada = Filter(id_user)
print(list(dada.filter.values())[0])
print(dada.browse(page=1)[0])
response = requests.get(list(dada.filter.values())[1], headers=headers)
print(response.status_code)
mama = dict(response.cookies.items())
# mama["_vinted_fr_session"] = non
print(response.status_code, mama)


didi = requests.get(dada.browse(page=1)[0], headers=headers, cookies=mama)
print(didi.status_code)
print(didi.json())
# print(response.status_code)
# print(
#     response.cookies.items(),
#     response.cookies,
#     type(response.cookies),
#     dict(response.cookies.items()),
# )
b = time()
asyncio.run(alt_main(dada.browse(page=1), cooks=mama))
final = time()
print(f"Temps d'exécution : {final - b} secondes")
