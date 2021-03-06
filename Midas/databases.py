from Midas.configs import (
    mongo_connection_info,
    default_db,
    raw_data_collection,
    sessions_collection,
    models_collection,
    postgres_connection_info as pg,
)
from hashlib import md5
import time
import pickle
from pymongo import MongoClient, ReturnDocument
import pandas as pd
from bson import ObjectId
from sqlalchemy import create_engine


def mongo_to_df(db, collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """
    mongo_conn = MongoClient(**mongo_connection_info)
    # Make a query to the specific DB and Collection
    database = mongo_conn[db]
    cursor = database[collection].find(query)["data"]

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df["_id"]

    return df


def get_headers(collection, db=default_db):
    return mongo_to_df(db, collection).tolist()


def load_df_to_postgres(df, table, **kwargs):
    engine = create_engine(
        f"postgresql://{pg['user']}@{pg['host']}:{pg['port']}/{pg['database']}"
    )
    df.to_sql(table, engine, **kwargs)


def postgres_to_df(query, **kwargs):
    engine = create_engine(
        f"postgresql://{pg['user']}@{pg['host']}:{pg['port']}/{pg['database']}"
    )
    return pd.read_sql(query, engine, **kwargs)


def upload_raw_data(session_id, raw_data):
    mi_raw_data = MongoInterface(default_db, raw_data_collection)

    raw_data_id = mi_raw_data.insert_records({"data": raw_data})

    update_session_data(session_id, dict(raw_data_ids=raw_data_id))
    return str(raw_data_id)


def update_session_data(session_id, push_dict):
    mi = MongoInterface(default_db, sessions_collection)
    return mi.update_records({"_id": ObjectId(session_id)}, {"$push": push_dict})


def create_new_session(session_obj):
    # session_obj here is a dict
    mi = MongoInterface(default_db, sessions_collection)
    return mi.insert_records(session_obj)


def get_session_data(session_id):
    mi = MongoInterface(default_db, sessions_collection)
    return mi.retrieve_records({"_id": ObjectId(session_id)})


def get_models_from_session(session_id):
    model_ids = get_session_data(session_id)["model_ids"]
    mi = MongoInterface(default_db, models_collection)

    model_filter = []
    for model in model_ids:
        model_filter.append({"_id": ObjectId(model)})

    return mi.retrieve_records(model_filter)


def get_model(model_id):
    mi = MongoInterface(default_db, models_collection)
    return mi.retrieve_records({"_id": ObjectId(model_id)})


def save_model(model):
    mi = MongoInterface(default_db, models_collection)

    model_id = mi.insert_records(
        {
            "pickled_model": model,
        }
    )
    return model_id


def update_model(model_id, update_values, operation="set"):
    mi = MongoInterface(default_db, models_collection)
    mi.update_records({"_id": ObjectId(model_id)}, {f"${operation}": update_values})


def delete_model(model_id):
    mi = MongoInterface(default_db, models_collection)
    mi.delete_records({"_id": ObjectId(model_id)})


def delete_session(session_id):

    print(f"session_id: {session_id}")
    mis = MongoInterface(default_db, sessions_collection)
    # we should be getting 1 session because objectids are unique
    session = mis.retrieve_records({"_id": ObjectId(session_id)})[0]
    count = mis.delete_records({"_id": ObjectId(session_id)})
    # delete associated model
    print(count)
    delete_model(session["model_id"])
    


def get_raw_data(session_id):
    raw_data_ids = get_session_data(session_id)["raw_data_ids"]
    mi = MongoInterface(default_db, raw_data_collection)

    raw_data_filter = []

    for _id in raw_data_ids:
        raw_data_filter.append({"_id": ObjectId(_id)})

    return mi.retrieve_records(raw_data_filter)


def raw_data_to_df(raw_data_id):
    mi = MongoInterface(default_db, raw_data_collection)
    data = mi.retrieve_records({"_id": ObjectId(raw_data_id)})["data"]
    df = pd.read_json(data, orient="records")

    return df


def get_all_sessions():
    mis = MongoInterface(default_db, sessions_collection)
    all_sessions = mis.retrieve_records({})
    print(all_sessions)
    model_data = []
    for session in all_sessions:
        # print("session: %s" % str(session["_id"]))
        model_data.append(
            {
                "session_id": session["_id"],
                "ml_algorithm": session["ml_algorithm"],
                "pretty_name": session["pretty_name"],
            }
        )

    print(model_data)
    return model_data


class MongoInterface:
    def __init__(self, db, collection):
        mongo_conn = MongoClient(**mongo_connection_info)
        database = mongo_conn[db]
        self.interface = database[collection]

    def insert_records(self, records):
        """
        simple method to insert one or many records
        """
        # short circuit for situation where we provided a single dict

        if type(records) == dict:
            result = self.interface.insert_one(records)
            return result.inserted_id
        elif type(records) == list and len(records) == 1:
            result = self.interface.insert_one(records[0])
            return result.inserted_id
        else:
            result = self.interface.insert_many(records)
            return result.inserted_ids

    def retrieve_records(self, _filter):
        """
        simple method to retrieve mongo records
        returns updated records (dicts)
        """
        return self.interface.find(_filter)

    def update_records(self, _filter, update_values):
        """
        simple method to update mongo records
        """
        if type(_filter) == dict:
            return self.interface.find_one_and_update(
                _filter,
                update_values,
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        elif type(_filter) == list and len(_filter) == 1:
            return self.interface.find_one_and_update(
                _filter[0],
                update_values[0],
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        else:
            self.interface.update_many(_filter, update_values, upsert=True)
            return self.interface.find(_filter)

    def delete_records(self, _filter):
        if type(_filter) == dict:
            result = self.interface.delete_one(_filter)
        elif type(_filter) == list and len(_filter) == 1:
            result = self.interface.delete_one(_filter[0])
        else:
            result = self.interface.delete_many(_filter)
        return result.deleted_count
