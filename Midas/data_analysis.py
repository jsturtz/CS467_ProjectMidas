from Midas.configs import mongo_connection_info
import numpy as np
from pymongo import MongoClient
import pandas as pd


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


def get_headers(collection, db='raw_data'):
    return mongo_to_df(db, collection).tolist()


def make_data_dictionary(collection, db='raw_data'):

    mongo_conn = MongoClient(**mongo_connection_info)
    in_data = mongo_to_df(mongo_conn[db], collection)

    # create a new dataframe for the data dictionary containing the feature list
    dd = pd.DataFrame(list(in_data),columns=['Feature'])

    #  add variable type to the data dictionary
    dd['Type'] = in_data.dtypes.tolist()

    # add count of distinct values to data dictionary
    dd['Distinct'] = in_data.nunique().tolist()

    # make lists for frequency counts and missing values
    freq_counts = []
    missing_counts = []

    # iterate through the columns
    for column in in_data:
        print(f'working on {column}')
        # get frequency counts
        vcs = in_data[column].value_counts(dropna=False).to_dict()

        # use binning if the feature is numeric and there are many unique values
        if len(vcs) > 10 and np.issubdtype(in_data[column].dtype,np.number):
            bins_data = in_data[column].value_counts(dropna=False, bins = 10)
            freq_counts.extend([(bins_data.to_dict())])

        # if many unique values, but categorical variable, only keep top 10 frequencies
        elif len(vcs) > 10:
            freq_counts.extend([in_data[column].value_counts(dropna=False)[:10].to_dict()])

        # for a small number of unique values, keep all frequencies
        else:
            freq_counts.extend([vcs])

        # obtain count of missing values
        if np.issubdtype(in_data[column].dtype,np.number):
            # for numeric variables, use isnull
            missing_counts.extend([in_data[column].isnull().sum()])
        else:
            missing_counts.extend([in_data[column].isna().sum()])

    # add count of missing values
    dd['Missing'] = missing_counts

    # Add minimum value for each feature (if applicable)
    dd = dd.merge(in_data.min().to_frame(), left_on=['Feature'], right_index=True, how='left')
    dd.rename(columns={dd.columns[-1]: 'Minimum'}, inplace=True)

    # Add maximum value for each feature (if applicable)
    dd= dd.merge(in_data.max().to_frame(), left_on=['Feature'], right_index=True, how='left')
    dd.rename(columns={dd.columns[-1]: 'Maximum'}, inplace=True)

    dd['Top Frequencies'] = freq_counts

    # set options so columns aren't truncated
    pd.set_option('display.max_colwidth', -1)
    
    # format for easier html templating
    dd_dict = dd[1:].to_dict()
    headers = [key for key in dd_dict.keys()]
    rows = [[val[key] for val in dd_dict.values()] for key in next(iter(dd_dict.values())).keys()]
    return {'headers': headers, 'rows': rows}
