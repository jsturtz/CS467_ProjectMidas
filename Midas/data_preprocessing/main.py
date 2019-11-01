import click
import pandas as pd
from pymongo import MongoClient
from sys import exit
from utils.data_dictionary import make_data_dictionary


mongo_connection_info = {
        'host': 'mongo',
        'port': 27017
        }


def mongo_to_df(db, collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Make a query to the specific DB and Collection
    cursor = db[collection].find({})

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df


@click.command()
@click.argument('db')
@click.argument('collection')
@click.argument('out_html')
def main(db, collection, out_html):
    # get data from mongo and store into dataframe
    mongo_conn = MongoClient(**mongo_connection_info)
    df = mongo_to_df(mongo_conn[db], collection)
    print(df.head())
    print(f'len: {len(df)}')
    make_data_dictionary(df, out_html)


if __name__ == '__main__':
    try:
        main()
    except:  # can add more specific exceptions to return specific errors
        raise
        exit(1)
