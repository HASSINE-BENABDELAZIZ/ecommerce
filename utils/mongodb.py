import logging
import os
import urllib

import pymongo
from django.conf import settings


def mongo_db():
    connection_instruction = f"mongodb://{settings.MONGO_USERNAME}:" + \
                             f"{urllib.parse.quote(settings.MONGO_PASSWORD)}" + \
                             f"@{settings.MONGO_HOST}:" + \
                             f"{settings.MONGO_PORT}/" \
                             + (f"?authSource={settings.MONGO_DB}"
                                if os.environ.get('PRODUCTION',
                                                  'on') == 'on' else "")
    client = pymongo.MongoClient(
        connection_instruction, retryWrites=False)
    mydb = client[settings.MONGO_DB]
    return mydb


def mongo_insert(collection_name: str, data: dict):
    db = mongo_db()
    mycol = db[collection_name]
    try:
        result = mycol.insert_one(data)
        return result
    except Exception:
        pass


def mongo_update(collection_name: str,
                 filter_query: dict,
                 data: dict,
                 *args,
                 **kwargs):
    db = mongo_db()
    mycol = db[collection_name]
    try:

        result = mycol.find_one_and_update(filter_query, data, *args, **kwargs)
        return result
    except Exception as e:
        logging.exception(e)
