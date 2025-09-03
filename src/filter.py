import logging
import re
from typing import Dict
from urllib.parse import parse_qs, urlparse, urlunparse

import couchdb
from pydantic import BaseModel, HttpUrl

from db.couch_items import couch, user_id

the_id = user_id


class InvalidURLException(Exception):
    """Exception raise when URL is not valid"""

    pass


class ExistingURLException(Exception):
    """Exception raise when URL already existing."""

    pass


class ExistingNameException(Exception):
    """Exception raise when Name already existing."""

    pass


class FilterModel(BaseModel):
    id: str
    filter: Dict[str, HttpUrl] = {}


class Filter:
    ALLOW_DOMAIN = re.compile(r"^https://www\.vinted\.(\w{2,3})/catalog\?(.*)$")

    def __init__(self, id: int) -> None:
        self.db = couch["users_filter"]
        self.id = str(id)
        self.filter = self.init_filter()

    @classmethod
    # get only the filter given an ID
    def get_filter(cls, id, db=couch["users_filter"]):
        file = db.get(str(id))
        if file is not None:
            return file["filter"]
        else:
            return

    def to_pydantic(self):
        # model to pydantic
        return FilterModel(
            id=self.id,
            filter=self.filter,
        )

    def is_valid_url(self, url):
        # Check on the URL, gotta be good shape
        return bool(self.ALLOW_DOMAIN.match(url))

    def init_filter(self):
        try:
            file = self.db.get(self.id)
            return file["filter"]
        except (
            TypeError,
            KeyError,
        ):  # TypeError si file=None, KeyError si pas "filter"
            logging.error(f"New account or no filter yet for {self.id}")
            return {}

    def add_url(self, name: str, url: str):
        # add url in self.filter given a name after checking if name or url already used
        if not self.is_valid_url(url):
            raise InvalidURLException(f"URL invalide : {url}")

        if url in self.filter.values():
            raise ExistingURLException(f"URL : {url} already exist")

        if name in self.filter.keys():
            raise ExistingNameException(f"Name : {name} already used")

        self.filter[name] = url

    def del_url(self, name: str):
        # del url in self.filter given a name which is a key
        if name in self.filter.keys():
            self.filter.pop(name)
        else:
            return

    def save_filter(self):
        try:
            filter = self.db.get(self.id)
            if filter:
                new_filter = {
                    "_id": str(self.id),
                    "_rev": filter["_rev"],
                    "filter": self.filter,
                }

                self.db.save(new_filter)
                print("MAJ filtre ")
                return

            else:
                filter = {"_id": str(self.id), "filter": self.filter}
                self.db.save(filter)
                print(f"[INFO] Création de {self.id}")
                return

        except couchdb.http.ResourceConflict:
            print(f"[ERROR] conflict for user: {self.id}")

    def transform(self, page, item):
        # url accessing the API of v by transforming an actual url
        # item is how many ... item u get into the json scrap from API's url
        url_API = []
        for url in self.filter.values():
            u = urlparse(url)

            new_path = u.path.replace("catalog", "api/v2/catalog/items")

            # parse query into a dictionary : {"brand_ids[]": "545..."}
            query_params = parse_qs(u.query, keep_blank_values=True)

            # remove []
            query_params_clean = {
                k.replace("[]", ""): v for k, v in query_params.items()
            }

            query_params_clean["order"] = ["newest_first"]
            query_params_clean["catalog_ids"] = query_params_clean.pop("catalog")
            query_params_clean.pop("disabled_personalization", None)

            # merge identic data separate by comma
            query_params_clean = {k: ",".join(v) for k, v in query_params_clean.items()}

            query_params_clean = {"per_page": str(item), **query_params_clean}
            query_params_clean = {"page": str(page), **query_params_clean}

            new_query = "&".join([f"{k}={v}" for k, v in query_params_clean.items()])
            new_url = urlunparse(u._replace(path=new_path, query=new_query))

            url_API.append(new_url)

        return url_API

    def feed(self, page=1, item=6):
        # the less items you scrap, the less data you consume, sounds cheap but
        # if you pay an IP provider/GB, it makes sense
        return self.transform(page, item)

    def browse(self, page, item=96):
        # all the items you can scrap from an json's API
        return self.transform(page, item)


abroad = (
    "https://www.vinted.de/catalog?time=1743437029&disabled_personalization=true&catalog_from=0&page=1&currency=EUR&catalog[]=1206&brand_ids[]=319730&price_to=169&order=merde",
    "https://www.vinted.pt/catalog?time=1743437313&catalog[]=2050&disabled_personalization=true&catalog_from=0&brand_ids[]=272719&page=1&order=newest_first&size_ids[]=208&status_ids[]=1&status_ids[]=2",
    "https://www.vinted.lt/catalog?time=1743437476&catalog[]=2050&disabled_personalization=true&catalog_from=0&brand_ids[]=872289&page=1&size_ids[]=208&size_ids[]=207&material_ids[]=44"
    "https://www.vinted.nl/catalog?time=1743437617&search_text=teddy%20santis&disabled_personalization=true&page=1&price_to=169&currency=EUR",
    "https://www.vinted.dk/catalog?time=1743437687&catalog[]=4&disabled_personalization=true&catalog_from=0&brand_ids[]=38437&page=1&size_ids[]=2&size_ids[]=3&size_ids[]=4&status_ids[]=1&status_ids[]=2&status_ids[]=6&color_ids[]=1&color_ids[]=20&color_ids[]=12&color_ids[]=15&color_ids[]=9&color_ids[]=27&color_ids[]=23&color_ids[]=14&color_ids[]=22",
)

name = ("nike", "adidas", "puma")

many = (
    "https://www.vinted.fr/catalog?search_text=&catalog[]=5&brand_ids[]=2367131&brand_ids[]=272719&brand_ids[]=47829&brand_ids[]=2318552&brand_ids[]=5589958&brand_ids[]=7263752&brand_ids[]=218132&brand_ids[]=51445&brand_ids[]=609050&brand_ids[]=3354969&brand_ids[]=461946&search_id=21453042887&order=newest_first&time=1748853496",
    "https://www.vinted.fr/catalog?search_text=&catalog[]=1231&size_ids[]=782&size_ids[]=783&size_ids[]=784&brand_ids[]=7319&brand_ids[]=272814&search_id=21483906252&order=newest_first&time=1748853545",
    "https://www.vinted.fr/catalog?search_text=&catalog[]=2050&brand_ids[]=369700&brand_ids[]=4756277&brand_ids[]=75090&brand_ids[]=72138&brand_ids[]=200474&brand_ids[]=576107&search_id=18098274779&order=newest_first&time=1748853624",
)


check = Filter(id=user_id)

# print(list(check.filter.values()))
to_scrap = check.browse(page=1)
print(to_scrap)
