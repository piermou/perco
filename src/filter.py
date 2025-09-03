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

    # @classmethod
    # def get_filter(cls, name, id):
    #     filters = cls.filters(id)
    #     for f in filters:
    #         if f.name == name:
    #             return f
    #     print("[INFO] pas de filtre à ce nom ...")
    #     return None

    # @classmethod
    # def del_filter(cls, name, id, couch=couch):
    #     filter = couch["filters"].view(
    #         "filter/filter_by_user_and_name", key=[id, name], include_docs=True
    #     )

    #     if filter:
    #         print("[INFO] filtre va être delete ...")
    #         for row in filter:
    #             doc = row.doc
    #             couch["filters"].delete(doc)
    #     else:
    #         print("[INFO] delete un filtre qui n'existe pas ...")
    #
    #

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
            print(
                f"[ERROR] Conflit détecté lors de la sauvegarde du filtre pour user {self.id}"
            )

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

            # Fusionner les valeurs identiques avec des virgules
            query_params_clean = {k: ",".join(v) for k, v in query_params_clean.items()}

            query_params_clean = {"per_page": str(item), **query_params_clean}
            query_params_clean = {"page": str(page), **query_params_clean}

            new_query = "&".join([f"{k}={v}" for k, v in query_params_clean.items()])
            new_url = urlunparse(u._replace(path=new_path, query=new_query))

            url_API.append(new_url)

        return url_API

    def feed(self, page=1, item=6):
        return self.transform(page, item)

    def browse(self, page, item=96):
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
# da = check.browse(page=1)
# print(da)
# for i, j in zip(name, many):
#     check.add_url(i, j)

# print(check.filter)

# check.save_filter()

dada = Filter.get_filter(user_id, couch["users_filter"])
# dada = couch["users_filter"].get(str(user_id))["filter"]

# print(dada)
# pourvoir = Filter.get_filter("frenchcoco", id)
# mama = pourvoir.urls
# print(pourvoir.browse(page=1))


# mama = Filter.get_filter(id=id, name="jaime")
# print(mama.to_feed())


# mama = Filter()
# for i in abroad:
#     mama.add_url(i)

# print(mama.to_feed())
# mama.name = "jeez"
# mama.save_filter()
#


# caca = Filter.get_filter(id=id, name="jeez", couch=couch)
# print(caca)
# # #

# vasavoir = couch["filters"].get("user:3374821553699556532:filter:jeez")
# print(vasavoir)

# miamia = couch["filters"].view("test/simple_view", key=id, include_docs=True)
# for i in miamia:
#     print(i.doc.get("urls"))
# print(miamia)

# Filter.del_filter("douch", str(id), couch)

# Filter.del_filter("abroad", str(id), couch)

# urlll = "https://www.vinted.frrzz/member/1558"
# dammmm = "https://www.vinted.fr/member/18544025"
# anotherone = "https://www.vinted.fr/catalog?search_text=&catalog[]=5&brand_ids[]=2367131&brand_ids[]=272719&brand_ids[]=47829&brand_ids[]=2318552&brand_ids[]=5589958&brand_ids[]=7263752&brand_ids[]=218132&brand_ids[]=51445&brand_ids[]=609050&brand_ids[]=180798&brand_ids[]=3354969&search_id=21453042887&order=newest_first&time=1743587819"

# abroad = (
#     "https://www.vinted.de/catalog?time=1743437029&disabled_personalization=true&catalog_from=0&page=1&currency=EUR&catalog[]=1206&brand_ids[]=319730&price_to=169&order=newest_first",
#     "https://www.vinted.pt/catalog?time=1743437313&catalog[]=2050&disabled_personalization=true&catalog_from=0&brand_ids[]=272719&page=1&order=newest_first&size_ids[]=208&status_ids[]=1&status_ids[]=2",
#     "https://www.vinted.lt/catalog?time=1743437476&catalog[]=2050&disabled_personalization=true&catalog_from=0&brand_ids[]=872289&page=1&size_ids[]=208&size_ids[]=207&material_ids[]=44"
#     "https://www.vinted.nl/catalog?time=1743437617&search_text=teddy%20santis&disabled_personalization=true&page=1&price_to=169&currency=EUR",
#     "https://www.vinted.dk/catalog?time=1743437687&catalog[]=4&disabled_personalization=true&catalog_from=0&brand_ids[]=38437&page=1&size_ids[]=2&size_ids[]=3&size_ids[]=4&status_ids[]=1&status_ids[]=2&status_ids[]=6&color_ids[]=1&color_ids[]=20&color_ids[]=12&color_ids[]=15&color_ids[]=9&color_ids[]=27&color_ids[]=23&color_ids[]=14&color_ids[]=22",
# )

# geez = FilterCreation()
# for i in abroad:
#     geez.add_url(i)
# geez.name = "wataaaa"
# geez.save_filter()


# pourvoir = FilterCreation()
# for i in abroad:
#     pourvoir.add_url(i)
# pourvoir.name = "mamacita"
# print(pourvoir.__dict__)
# pourvoir.save_filter()
# xssss = [
#     "https://www.vinted.fr/api/v2/catalog/items?search_text=usa&brand_ids=1775&search_id=12043902536&order=newest_first&time=1743084178&catalog_ids=2050",
#     "https://www.vinted.fr/api/v2/catalog/items?search_text=990v3&size_ids=783,784&brand_ids=1775,6096742,6430888&search_id=21794237624&order=newest_first&time=1743413361&catalog_ids=1231",
#     "https://www.vinted.fr/api/v2/catalog/items?search_text=acg&size_ids=207,208,209,5,4,6&brand_ids=53,687713,128360&search_id=21453862878&order=newest_first&time=1742839653",
#     "https://www.vinted.fr/api/v2/catalog/items?search_text=&size_ids=782,783,784&brand_ids=7319,272814&search_id=21483906252&order=newest_first&time=1742839652&catalog_ids=1231",
#     "https://www.vinted.fr/api/v2/catalog/items?brand_ids=319730&search_id=21870165653&order=newest_first&time=1743342013&catalog_ids=1206",
# ]


# u = urlparse(urlll)
# print(u.netloc)
# machin = couch["filters"]

# damnit = machin["user:3374821553699556532:filter:abroad"]["urls"]
# damnit = urlll
# machin.save(machin["user:3374821553699556532:filter:abroad"])

# print(machin["urls"])


# urll = UrlTransfomer(one_url)
# print(urll.len)
# oui = urll.all_filter()
# print(oui)
