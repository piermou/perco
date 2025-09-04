import asyncio
import json
import json as js
import logging
import time
from datetime import datetime

import aiohttp
import couchdb

from db.couch_items import COUCHDB_URL, DB_NAME

DB_NAME = "test_db"

with open("src/json2.json", "r") as f:
    mama = js.load(f)


async def save_into_couch(canap, doc, sem):
    # you might want to save item into your couch in a async fashion
    try:
        canap["gson"].save(doc)
        print(f"Document {doc['_id']} inséré avec succès")
    except couchdb.http.ResourceConflict:
        canap["gson"].changes()
        print(f"Document {doc['_id']} déjà existant")


async def save_item_couch(session, item):
    # trying to fetch data via async library because dedicted one "couchdb" is not
    url = f"{COUCHDB_URL}/{DB_NAME}/{item['_id']}"
    header = {"Content-Type": "application/json"}

    async with session.put(url, data=json.dumps(item), headers=header) as resp:
        if resp.status == 201:
            print(f"Document {item['_id']} inséré")
        elif resp.status == 409:
            print(f"⚠️ Document {item['_id']} déjà existant, on ignore")
        else:
            text = await resp.text()
            raise Exception(f"Erreur {resp.status}: {text}")


async def main(items):
    async with aiohttp.ClientSession() as session:
        tasks = [save_item_couch(session, item) for item in items]
        await asyncio.gather(*tasks)


def json_component(json_item):
    # just chosing the right variable to stock
    price = json_item.get("price", {}) or {}
    total_price = json_item.get("total_item_price", {}) or {}
    photo = json_item.get("photo", {}) or {}
    high_res = photo.get("high_resolution", {}) or {}

    return {
        "_id": str(json_item.get("id")),
        "title": json_item.get("title"),
        "url": json_item.get("url"),
        "brand_title": json_item.get("brand_title"),
        "size": json_item.get("size_title"),
        "price": {
            "raw_price": price.get("amount"),
            "total_price": total_price.get("amount"),
            "currency": price.get("currency_code"),
        },
        "photo": photo.get("url"),
        "status": json_item.get("status"),
        "timestamp": high_res.get("timestamp"),
        "favourite_count": json_item.get("favourite_count"),
    }


def json_file(json):
    try:
        items_list = json["items"]

        items_list_transform = [json_component(item) for item in items_list]

        return items_list_transform

    except TypeError as e:
        logging.exception(
            f"JSON does not have items key, so surely the requests to the API has been blocked {e}"
        )
        return []


def transform_item(json):
    # json : dict -> list -> dict
    trans = json["items"]
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


# with open("src/json2.json", "r") as f:
#     mama = js.load(f)

# # damn = mama["items"][0]
# dude = mama["items"]
# print(type(dude))
# xd = json_file(dude)

# print(xd[0])


def per_id(json):
    try:
        # json : dict -> list -> dict
        trans = json["items"]
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


plus = json_file(mama)

asyncio.run(main(plus))

# print(json_file(mama))
