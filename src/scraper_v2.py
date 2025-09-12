import asyncio
import json
import logging
from pathlib import Path
from time import time

import aiohttp
from curl_cffi import requests

from config import REDIS_PORT, headers, id_user
from db.cookies import get_cookie
from src.filter import Filter
from src.item_json import json_file, save_item_couch


async def fetch_one(session: requests.AsyncSession, url: str):
    try:
        r = await session.get(url)
        print(r.status_code)
        r.raise_for_status()
        return r.json()  # ou r.text si tu veux brut
    except Exception as e:
        print(f"erreur sur {url}: {e}")


async def fetch_image(session: aiohttp.ClientSession, item: dict, sem):
    # download one image, asynchronously
    item_id = item.get("_id")
    image_url = item.get("photo")
    if not item_id or not image_url:
        logging.warning(f"Item avec ID {item_id} est manquant ou sans photo, ignoré.")
        return

    img_filename = Path("images") / f"{item_id}.jpg"

    if img_filename.exists():
        print(f"L'image pour l'ID {item_id} existe déjà, saut du téléchargement.")
        logging.info(
            f"L'image pour l'ID {item_id} existe déjà, saut du téléchargement."
        )
        return

    try:
        async with sem:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(img_filename, "wb") as img_file:
                        img_file.write(await response.read())  # download image
                    print(f"Image {item_id} téléchargée avec succès !")
                else:
                    logging.error(
                        f"Erreur HTTP {response.status} pour l'image {image_url}"
                    )
    except aiohttp.ClientConnectionError as e:
        logging.error(f"Erreur lors du téléchargement de l'image {image_url}: {e}")


async def main(urls):
    response = requests.get("https://www.vinted.com", headers=headers)
    cookies = dict(response.cookies.items())
    sem = asyncio.Semaphore(32)

    async with requests.AsyncSession(headers=headers, cookies=cookies) as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    async with aiohttp.ClientSession(cookies=cookies) as aiosession:
        jsons = tuple(map(json_file, results))

        save_tasks = [
            save_item_couch(aiosession, item) for json in jsons for item in json
        ]
        await asyncio.gather(*save_tasks)

        image_tasks = [
            fetch_image(aiosession, item, sem) for json in jsons for item in json
        ]
        await asyncio.gather(*image_tasks)


if __name__ == "__main__":
    dude = Filter(id=id_user)
    print(dude.browse(page=1)[0])
    b = time()
    asyncio.run(main(dude.browse(page=1)))
    final = time()
    print(f"Temps d'exécution : {final - b} secondes")
