import asyncio
import logging
import os
import random
from pathlib import Path

import aiohttp

from db.redis_pubsub import r
from src.item_json import json_file, save_item_couch

oui = "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhcHBfaWQiOjQsImF1ZCI6ImZyLmNvcmUuYXBpIiwiY2xpZW50X2lkIjoid2ViIiwiZXhwIjoxNzU3MDMwMDE2LCJpYXQiOjE3NTcwMjI4MTYsImlzcyI6InZpbnRlZC1pYW0tc2VydmljZSIsInB1cnBvc2UiOiJhY2Nlc3MiLCJzY29wZSI6InB1YmxpYyIsInNpZCI6IjU1MGNjY2QzLTE3NTcwMjI4MTYifQ.BR3bYE9dFJ03qi7PViyAnS1LN3k1c6cxz5_zxfPnQjFV8-VQpe4P-moZ5iW6pLduXUZIr5ySUxGnPUtvLUbY7NJ5SYQ6z6RI6giO4Q6-nJeICqkMyaDBYD8dgkiaLIEvKst9jB_yYrGogwtnkxoaZhWm0sKek-dGPRD865Xf2JWV9LTxXunrgOxsVIcO_nHKNxvLFdbGNFQnmd8d94xIRAR602a1D2bL37xynMXuvtKzoTuTJG_XFF9VU7ssnqW1vhQpR3o-mn65JesFC6Y06bwL8xRA2doy9JENiOHwCPNLhdoVR78zWZz-n5e9CIzfP6dljq4qjZ_re4nAuuIhzQ"


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/11.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
]


async def fetch_json(session, urls):
    # fetch json in async
    try:
        async with session.get(urls) as response:
            if response.status == 200:
                print("[INFO] json fetched")
                return await response.json()
            elif response.status in [401, 403]:
                r.delete("access_token_web")
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


async def alt_main(urls):
    # damn = random.randint(33, 66)
    sem = asyncio.Semaphore(1000)
    headers = {"User-Agent": str(random.choices(user_agents))}
    # cookies = {"access_token_web": str(cookie_tes(r, headers=headers))}
    cookies_dif = {"access_token_web": oui}
    async with aiohttp.ClientSession(headers=headers, cookies=cookies_dif) as session:
        # lauch the process with hopefully the right cookie
        json_tasks = [fetch_json(session, url) for url in urls]
        json_results = await asyncio.gather(*json_tasks)

        jsons = tuple(map(json_file, json_results))

        save_tasks = [save_item_couch(session, item) for json in jsons for item in json]
        await asyncio.gather(*save_tasks)
        # transform and save into couch before images because it could lead to fail
        # because fetch image depend on these change (change of key: value pair)

        image_tasks = [
            fetch_image(session, item, sem) for json in jsons for item in json
        ]
        await asyncio.gather(*image_tasks)


# b = time()
# asyncio.run(alt_main(dada.browse(page=1)))
# final = time()
# print(f"Temps d'exécution : {final - b} secondes")
