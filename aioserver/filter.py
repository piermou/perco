import logging
import re
from typing import Dict
from urllib.parse import parse_qs, urlparse, urlunparse

import couchdb
from pydantic import BaseModel, HttpUrl

from config import couch, id_user


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
            if file is not None:
                return file["filter"]
            else:
                return {}
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
        # page is what ... page of the url you are scraping to
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
