from Midas.configs import mongo_connection_info, default_db, postgres_connection_info as pg
from pymongo import MongoClient, ReturnDocument
import pandas as pd


def mongo_to_df(db, collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """
    mongo_conn = MongoClient(**mongo_connection_info)
    # Make a query to the specific DB and Collection
    database = mongo_conn[db]
    cursor = database[collection].find({})

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df


def get_headers(collection, db=default_db):
    return mongo_to_df(db, collection).tolist()


def load_df_to_postgres(df, table, **kwargs):
    engine = create_engine(f"postgresql://{pg['user']}@{pg['host']}:{pg['port']}/{pg['database']}")
    df.to_sql(table, engine, **kwargs)


def postgres_to_df(query, **kwargs):
    engine = create_engine(f"postgresql://{pg['user']}@{pg['host']}:{pg['port']}/{pg['database']}")
    df = pd.read_sql(query, engine, **kwargs)



class MongoInterface:

    def __init__(self, db, collection):
        mongo_conn = MongoClient(**mongo_connection_info)
        database = mongo_conn[db]
        self.interface = database[collection]


    def insert_records(self, records):
        '''
        simple method to insert one or many records
        '''
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
        '''
        simple method to retrieve mongo records
        returns updated records (dicts)
        '''
        if type(_filter) == dict:
            return self.interface.find_one(_filter)
        elif type(_filter) == list and len(_filter) == 1:
            return self.interface.find_one(_filter[0])
        else:
            return self.interface.find(_filter)


    def update_records(self, _filter, update_values):
        '''
        simple method to update mongo records
        '''
        if type(_filter) == dict:
            return self.interface.find_one_and_update(_filter, update_values, return_document=ReturnDocument.AFTER)
        elif type(_filter) == list and len(_filter) == 1:
            return self.interface.find_one_and_update(_filter[0], update_values[0], return_document=ReturnDocument.AFTER)
        else:
            self.interface.update_many(_filter, update_values)
            return self.interface.find(_filter)


    def delete_records(self, _filter):
        if type(_filter) == dict:
            result = self.interface.delete_one(_filter)
        elif type(_filter) == list and len(_filter) == 1:
            result = self.interface.delete_one(_filter[0])
        else:
            result = self.interface.delete_many(_filter)
        return result.deleted_count