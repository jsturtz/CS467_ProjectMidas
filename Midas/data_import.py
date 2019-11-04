from bson.json_util import loads
from hashlib import md5
import pandas as pd
from Midas.configs import mongo_connection_info
from pymongo import MongoClient
from sys import exit
import time


def store_raw_data(abs_path, database_name='raw_data'):

    # all files are stored internally in /var/tmp
    mongo_conn = MongoClient(**mongo_connection_info)
    db = mongo_conn[database_name]

    # collection_name determined by filename, create unique collection
    collection_name = f'{md5(os.path.basename(abs_path).encode()).hexdigest()}_{int(time.time())}'

    collection = db[collection_name]

    df = pd.read_csv(abs_path, header=0, index_col=False)
    df_json = df.to_json(orient='records')
    insert_ids = collection.insert_many(loads(df_json))

    return collection_name
