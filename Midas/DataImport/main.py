import psycopg2
from pymongo import MongoClient


def main():
    # connect to datasources
    postgres_connection_info = {
            'host': 'postgres',
            'port': 5432,
            'user': 'postgres',
            'database': 'postgres'
            }
    mongo_connection_info = {
            'host': 'mongo',
            'port': 27017
            }

    with psycopg2.connect(**postgres_connection_info) as conn:
        # use conn here
        print('sql run!')

    mongo_conn = MongoClient(**mongo_connection_info)
    # mongo conn here


if __name__ == '__main__':
    main()

