from bson.json_util import loads
import click
import pandas as pd
from pymongo import MongoClient
from sys import exit


@click.command()
@click.argument('filename', type=click.Path())
@click.argument('database_name')
@click.argument('collection_name')
def main(filename, database_name, collection_name):
    # all files are stored internally in /var/tmp
    mongo_connection_info = {
            'host': 'mongo',
            'port': 27017
            }

    mongo_conn = MongoClient(**mongo_connection_info)
    db = mongo_conn[database_name]
    collection = db[collection_name]

    df = pd.read_csv(filename, header=0, index_col=False)
    df_json = df.to_json(orient='records')
    insert_ids = collection.insert_many(loads(df_json))


if __name__ == '__main__':
    try:
        main()
    except:  # can add more specific exceptions to return specific errors
        raise
        exit(1)
