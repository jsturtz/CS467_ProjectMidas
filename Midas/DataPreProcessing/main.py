import dask.dataframe as dd
import time

start_time = time.time()
train_transaction = dd.read_csv('train_transaction.csv')
train_id = dd.read_csv('train_identity.csv')

joined_data = train_transaction.merge(train_id, how='left', on='TransactionID')
print(f'Took {time.time() - start_time}')

print(f'{joined_data.shape}')
print(f'{joined_data.head()}')
print(f'Took {time.time() - start_time}')
