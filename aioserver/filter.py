import logging
import re
from functools import lru_cache, partialmethod, singledispatch
from urllib.parse import parse_qs, urlparse, urlunparse

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models import Url, User
from config import engine


class PGContext:
    #
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def __enter__(self):
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logging.error(f"Error SQLAlchemy: {exc_value}")
            self.session.rollback()
        self.session.close()


class Filter:
    #
    ALLOW_DOMAIN = re.compile(r"^https://www\.vinted\.(\w{2,3})/catalog\?(.*)$")

    def __init__(self, email: str) -> None:
        #
        self.filter = []
        self.email = email
        with PGContext() as session:
            stmt = select(User).where(User.email == self.email)
            user = session.scalars(stmt).first()
            if not user:
                raise ValueError(f"No user for {self.email}")
            self.user_id = user.id

    def validation_url(self, url):
        # Check on the URL
        return bool(self.ALLOW_DOMAIN.match(url))

    def insert_url(self, name: str, url: str):
        #
        if self.validation_url(url) is True:
            with PGContext() as session:
                new_url = Url(user_id=self.user_id, name=name, url=url)
                session.add(new_url)
                try:
                    session.commit()
                    logging.info("✅ Url successfully added.")

                except sqlalchemy.exc.IntegrityError:
                    session.rollback()
                    logging.error(f"⚠️ already has an url with name: {name}")
        else:
            raise SyntaxError(f"URL invalide : {url}")

    def delete_url(self, name: str):
        #
        with PGContext() as session:
            stmt = select(Url).where(Url.user_id == self.user_id, Url.name == name)
            old_url = session.scalars(stmt).first()

            if old_url is None:
                logging.error(f"⚠️ No url with name: {name}")
                return

            session.delete(old_url)

            try:
                session.commit()
                logging.info("✅ Url successfully deleted.")
            except Exception as e:
                session.rollback()
                logging.error(f"⚠️ Error while deleting url {name}: {e}")

    def delete_urls(self, names: list[str]):
        #
        for name in names:
            self.delete_url(name)

    def get_filter(self):
        #
        with PGContext() as session:
            stmt = select(Url.url).where(Url.user_id == self.user_id)
            filter = session.scalars(stmt).all()

        if filter:
            logging.info(f"✅ Retrieved {len(filter)} urls for user: {self.user_id}")

        else:
            logging.info(f"⚠️ No urls yet for user: {self.user_id}")

        self.filter = filter

    def transform_url(self, page, item):
        """
        Transform an url to another one in order to request vinted's API.
        Item is how many items you get into the json scrap from an url.
        Page is which page of the url you are scraping.
        """
        url_API = []
        for url in self.filter:
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

    feed = partialmethod(transform_url, page=1, item=6)
    """
    The less items you scrap,the faster it is and the less data you consume,
    handy if you have a pay as you go subscription from your IP provider or
    to serve items with a minimum of delay...
    """

    browse = partialmethod(transform_url, item=96)
    """
    All the items you can scrap from an json's API, I believe you can
    push further but at what cost...
    """
