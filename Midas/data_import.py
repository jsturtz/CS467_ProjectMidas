from bson.json_util import loads
import pandas as pd
import os
from Midas.databases import MongoInterface
from Midas.configs import default_db, raw_data_collection


# writes to absolute path and then dumps into mongo
def handle_uploaded_file(filefield, session_id):
    path = os.getcwd() + "/datastores/csv/"
    print(path)
    with open(path + filefield.name, "wb+") as destination:
        for chunk in filefield.chunks():
            destination.write(chunk)
    return store_raw_data(path + filefield.name, session_id)


def store_raw_data(abs_path):
    # all files are stored internally in /var/tmp
    df = pd.read_csv(abs_path, header=0, index_col=False)
    df_json = df.to_json(orient="records")

    mi = MongoInterface(default_db, raw_data_collection)

    # import as value to "data" key
    insert_id = mi.insert_records({"data": loads(df_json)})
    return insert_id
