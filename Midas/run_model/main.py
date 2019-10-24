import psycopg2


def main():
    # connect to datasources
    postgres_connection_info = {
            'host': 'postgres',
            'port': 5432,
            'user': 'postgres',
            'database': 'postgres'
            }

    with psycopg2.connect(**postgres_connection_info) as conn:
        # use conn here
        print('sql run!')


if __name__ == '__main__':
    main()

