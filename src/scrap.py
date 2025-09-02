import asyncio
import logging
import os
import random
import time
from datetime import datetime

import aiohttp

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/11.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
]


def transform_items(ajson):
    # ajson : dict -> list -> dict
    trans = ajson["items"]
    # trans list of dict
    final = {str(item["id"]): item for item in trans}
    # dict of dict with unique id
    for i in list(final.keys()):
        final[i] = {
            "id": final[i].get("id"),
            "title": final[i].get("title"),
            "price": final[i].get("price").get("amount"),
            "total": final[i].get("total_item_price").get("amount"),
            "currency": final[i].get("price").get("currency_code"),
            "brand_title": final[i].get("brand_title"),
            "url": final[i].get("url"),
            "photo": final[i].get("photo", {}).get("url"),  # Gestion photo si absent
            "size": final[i].get("size_title"),
            "status": final[i].get("status"),
            "timestamp": time.time(),
            "date": datetime.now().strftime("%d-%m-%Y"),
        }

    return final


def per_id(ajson):
    try:
        # ajson : dict -> list -> dict
        trans = ajson["items"]
        # trans list of dict
        final = {str(item["id"]): item for item in trans}
        # dict of dict with unique id
        for i in list(final.keys()):
            final[i] = {
                "id": final[i].get("id"),
                "title": final[i].get("title"),
                "price": final[i].get("price").get("amount"),
                "total": final[i].get("total_item_price").get("amount"),
                "currency": final[i].get("price").get("currency_code"),
                "brand_title": final[i].get("brand_title"),
                "url": final[i].get("url"),
                "photo": final[i]
                .get("photo", {})
                .get("url"),  # Gestion photo si absent
                "size": final[i].get("size_title"),
                "status": final[i].get("status"),
                "timestamp": time.time(),
                "date": datetime.now().strftime("%d-%m-%Y"),
            }

        return final
    except KeyError as e:
        logging.exception(f"Clé manquante dans le JSON : {e}")
    except TypeError:
        logging.exception("Erreur de type : Le JSON doit être un dictionnaire Python")
    except Exception as e:
        logging.exception(f"Erreur inattendue : {e}")

    return None  # Retourne None en cas d'erreur


async def save_into_couch(canap, doc, sem):
    # async with sem:  # Limiter les connexions simultanées
    try:
        canap["gson"].save(doc)
        print(f"Document {doc['_id']} inséré avec succès")
    except couchdb.http.ResourceConflict:
        canap["gson"].changes()
        print(f"Document {doc['_id']} déjà existant")


async def fetch_json(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            print("[INFO] json bien récup")
            return await response.json()
        elif response.status in [401, 403]:
            r.delete("access_token_web")
            return "COOKIE_INVALID"
        else:
            print(f"[INFO] Réponse incorrecte sur {url}")
            return None


async def fetch_image(session, item, sem):
    """Télécharge une seule image asynchronement."""
    item_id = item.get("id")
    image_url = item.get("photo")
    if not item_id or not image_url:
        logging.warning(f"Item avec ID {item_id} est manquant ou sans photo, ignoré.")
        return

    img_filename = os.path.join("images", f"{item_id}.jpg")

    if os.path.exists(img_filename):
        print(f"L'image pour l'ID {item_id} existe déjà, saut du téléchargement.")
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


poufi = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


async def alt_main(urls):
    damn = random.randint(33, 66)
    vaasy = 66
    sem = asyncio.Semaphore(vaasy)
    headers = {"User-Agent": poufi}
    cookies = {"access_token_web": str(cookie_tes(r, poufi))}

    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        # Lancer toutes les tâches avec le bon cookie
        json_tasks = [fetch_json(session, url) for url in urls]
        json_results = await asyncio.gather(*json_tasks)
        print(json_results)
        for gson, i in json_results, len(json_results):
            with open(f"json{i}", "w", encoding="utf-8") as f:
                f.write(gson)

        jsons = tuple(map(transform_items, json_results))

        save_tasks = []
        # for json in jsons:
        #     for key, value in json.items():
        #         doc = {"_id": key}
        #         doc.update(value)
        #         save_tasks.append(save_into_couch(couch, doc, sem))

        # image_tasks = [
        #     fetch_image(session, item, sem)
        #     for json_data in jsons
        #     for item in json_data.values()
        # ]
        # await asyncio.gather(
        #     *save_tasks, *image_tasks
        # )  # Lancer tous les téléchargements en parallèle


id = "3374821553699556532"

mama = Filter.get_filter("frenchcoco", id)
print(mama.browse(2))

# client = requests.get(
#     url="https://www.vinted.fr/api/v2/catalog/items?page=1&per_page=96&search_text=&brand_ids=2367131,272719,47829,2318552,5589958,7263752,218132,51445,609050,3354969,461946&search_id=21453042887&order=newest_first&time=1748853496&catalog_ids=5",
#     headers=godesse,
#     cookies=cookies,
# )


# cookies = {
#     "access_token_web": str(client.cookies.get("access_token_web")),
#     "refresh_token_web": str(client.cookies.get("refresh_token_web")),
# }


# print(cookies, client.status_code, client.text)

# # headers = {"User-Agent": user_agents[0]}
# myurl = "https://www.vinted.fr/api/v2/catalog/items?page=1&per_page=96&time=1748857312&search_text=&catalog_ids=5&order=newest_first&catalog_from=0&size_ids=&brand_ids=2367131,272719,47829,2318552,5589958,7263752,218132,51445,609050,3354969,461946&status_ids=&color_ids=&patterns_ids=&material_ids="

# response = requests.get(myurl)
# print(response.status_code)
# client = curl_cffi.Session()

# client.get("https://www.vinted.com")

# print(client.cookies)


# choooose = cookie_tes(client=r, headers=headers)
# cook = {"access_token_web": str(choooose)}

# response = requests.get(url=myurl, cookies=cook, headers=headers)
# print(response.json)
# print(mama.browse(page=1))
# b = time.time()
# asyncio.run(alt_main(mama.browse(page=1)))
# final = time.time()
# print(f"Temps d'exécution : {final - b} secondes")
