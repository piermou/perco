import json
import logging

import redis
from curl_cffi import requests

from config import REDIS_PORT, headers, id_user
from src.filter import Filter


def get_cookie(client, headers, user_id):
    # depending on the cookie's gestion, either stock him on a redis cache
    # or keep it on the session if running a dedicated server for the scrap work
    url = "https://www.vinted.com"
    address_cookie: str = f"user:{user_id}"

    try:
        raw = client.get(address_cookie)
        if raw is not None:
            cookie_value = raw.decode("utf-8")
            logging.info("cookie exist, and is delicious ...")
            print("cookie exist, and is delicious ...")
            return cookie_value

        logging.info("[INFO] cookie does not exist, reload ...")
        response = requests.get(url, headers=headers)
        cookie_value = dict(response.cookies.items())
        print(response.status_code)
        if response.status_code != [403, 406, 404]:
            client.set(address_cookie, json.dumps(cookie_value), ex=1800)
            print("reloaded")
            return cookie_value

    except redis.ConnectionError as e:
        logging.error(f"Can't connect to redis : {e}")
        raise


if __name__ == "__main__":
    xd = get_cookie(REDIS_PORT, headers, id_user)
    dada = Filter(id=id_user)
    resp = requests.get(
        "https://images1.vinted.net/t/03_01b11_utDVV9UaviPEBR1inToWDXt6/f800/1756765632.jpeg?s=ba0133a7a0bc25b785409c16fd46ce2e3176c8c2"
    )
    print(resp.status_code)
    print(xd)
