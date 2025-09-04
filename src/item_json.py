import asyncio
import json
import logging

import aiohttp

from db.couch_items import COUCHDB_URL, DB_NAME


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
