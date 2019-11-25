from bson.json_util import loads
from hashlib import md5
import pandas as pd
from Midas.configs import mongo_connection_info, default_db
import os
from pymongo import MongoClient
from sys import exit
import time

# absolute path to directory to store csvs

# writes to absolute path and then dumps into mongo
def handle_uploaded_file(filefield):
  path =  os.getcwd() + "/datastores/csv/"
  print(path)
  with open(path + filefield.name, 'wb+') as destination:
    for chunk in filefield.chunks():
      destination.write(chunk)
  return store_raw_data(path + filefield.name)

def store_raw_data(abs_path, database_name=default_db):

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
