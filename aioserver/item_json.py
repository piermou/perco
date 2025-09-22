import logging


def json_raw(json_item: dict) -> dict:
    # just chosing the right variable to stock
    price = json_item.get("price", {}) or {}
    total_price = json_item.get("total_item_price", {}) or {}
    photo = json_item.get("photo", {}) or {}
    high_res = photo.get("high_resolution", {}) or {}

    json_arrange = {
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
        # variable to be update
        "favourite_count": json_item.get("favourite_count"),
        "user_id_footprint": [],
    }

    return json_arrange


def json_fetched(json):
    try:
        items_list = json["items"]
        items_list_transform = [json_raw(item) for item in items_list]
        return items_list_transform

    except KeyError as e:
        logging.error(
            f"JSON does not have items key, so surely the requests to the API has been blocked {e}"
        )
        return []
