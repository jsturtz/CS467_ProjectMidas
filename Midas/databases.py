from Midas.configs import (
    mongo_connection_info,
    default_db,
    raw_data_collection,
    sessions_collection,
    models_collection,
    cleaning_configs_collection,
    postgres_connection_info as pg)
from pymongo import MongoClient, ReturnDocument
import pandas as pd
from bson import ObjectId


def mongo_to_df(db, collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """
    mongo_conn = MongoClient(**mongo_connection_info)
    # Make a query to the specific DB and Collection
    database = mongo_conn[db]
    cursor = database[collection].find(query)['data']

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


def upload_raw_data(session_id, raw_data):
    mi_raw_data = MongoInterface(default_db, raw_data_collection)

    raw_data_id = mi_raw_data.insert_records(
        {'data': raw_data}
    )

    update_session_data(session_id, dict(raw_data_ids=raw_data_id))
    return str(raw_data_id)


def update_session_data(session_id, push_dict):
    mi = MongoInterface(default_db, sessions_collection)
    return mi.update_records({'_id': ObjectId(session_id)}, {'$push': push_dict})


def create_new_session():
    mi = MongoInterface(default_db, sessions_collection)
    return str(mi.insert_records(
            {
                'raw_data_ids': [],
                'model_ids': []
            }
        )
    )

def get_session_data(session_id):
    mi = MongoInterface(default_db, sessions_collection)
    return mi.retrieve_records(
        {'_id': ObjectId(session_id)}
    )


def get_models_from_session(session_id):
    model_ids = get_session_data(session_id)['model_ids']
    mi = MongoInterface(default_db, models_collection)

    model_filter = []
    for model in model_ids:
        model_filter.append({'_id': ObjectId(model)})

    return mi.retrieve_records(model_filter)


def get_model(_filter):
    mi = MongoInterface(default_db, models_collection)
    
    if '_id' in _filter.keys():
        # formatting for mongo
        _filter['_id'] = ObjectId(_filter['_id'])

    return mi.retrieve_records(_filter)


def save_model(model, dataset_id, pretty_name, results):
    pickled_model = pickle.dumps(model)
    model_id = f'{md5(pickled_model.encode()).hexdigest()}_{int(time.time())}'
    mi = MongoInterface(default_db, models_collection)

    mi.insert_records(
        {
        'model_id': model_id,
        'pickled_model': pickled_model,
        'dataset_id': dataset_id,
        'results': results
        }
    )
    return model_id


def get_raw_data(session_id):
    raw_data_ids = get_session_data(session_id)['raw_data_ids']
    mi = MongoInterface(default_db, raw_data_collection)

    raw_data_filter = []

    for _id in raw_data_ids:
        raw_data_filter.append({'_id': ObjectId(_id)})

    return mi.retrieve_records(raw_data_filter)


def raw_data_to_df(raw_data_id):
    from pandas.io.json import json_normalize
    mi = MongoInterface(default_db, raw_data_collection)
    data = mi.retrieve_records({'_id': ObjectId(raw_data_id)})['data']
    df = pd.read_json(data, orient='records')

    return df


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
            return self.interface.find_one_and_update(_filter, update_values, upsert=True, return_document=ReturnDocument.AFTER)
        elif type(_filter) == list and len(_filter) == 1:
            return self.interface.find_one_and_update(_filter[0], update_values[0], upsert=True, return_document=ReturnDocument.AFTER)
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