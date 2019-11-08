from Midas.configs import mongo_connection_info
from pymongo import MongoClient
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


def get_headers(collection, db='raw_data'):
    return mongo_to_df(db, collection).tolist()
