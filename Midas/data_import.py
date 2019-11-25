from bson.json_util import loads
from hashlib import md5
import pandas as pd
from Midas.configs import mongo_connection_info, default_db, raw_data_collection
from Midas.databases import upload_raw_data
import os
from pymongo import MongoClient
from sys import exit
import time

# absolute path to directory to store csvs

# writes to absolute path and then dumps into mongo
def handle_uploaded_file(filefield, session_id):
  path =  os.getcwd() + "/datastores/csv/"
  print(path)
  with open(path + filefield.name, 'wb+') as destination:
    for chunk in filefield.chunks():
      destination.write(chunk)
  return store_raw_data(path + filefield.name, session_id)


def store_raw_data(abs_path, session_id):
    df = pd.read_csv(abs_path, header=0, index_col=False)
    df_json = df.to_json(orient='records')

    return upload_raw_data(session_id, df_json)
