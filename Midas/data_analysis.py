from Midas.configs import mongo_connection_info
from pymongo import MongoClient
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import os


def mongo_to_df(db, collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

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
    return __format_dataframe(dd)


def is_categorical(feature):
    return True

def make_feature_details(feature, collection):

    # TODO: Probably shouldn't hardcode the outcome field here
    plot = make_plot(feature, "isFraud", 25, collection) 
    summ = make_summary(feature, "isFraud", collection)
    freq = make_frequencies(feature, "isFraud", 25, collection)
    return {'plot': plot, 'summary': summ, 'frequency': freq}
    # return {dtype: 'numeric', "plot": plot, "summ": summ, "freq": freq}

# TODO: make_plot, make_summary, and make_frequency are ALL broken. Must fix these
# Need to fix this function so that it properly queries mongo only for one feature and then does its thing

# Should return a string indicating the location of the saved image
def make_plot(feature, outcome, rows_limit, collection, db='raw_data'):
    path = os.getcwd() + '/static/images/'
    
    # TODO: Figure out how to query mongo by column rather than getting all the data. That's what 'query' is for right?
    mongo_conn = MongoClient(**mongo_connection_info)
    in_data = mongo_to_df(mongo_conn[db], collection)

    print("***************ALL DATA ****************")
    print(in_data)

    if in_data[feature].count() > 0:
        if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
            try:
                fig, ax = plt.subplots(figsize=(10, 10))
                for group in in_data[outcome].unique():
                    sns.distplot((in_data.dropna(subset=[feature])).loc[in_data[outcome] == group, feature],
                                     kde=False, ax=ax, label=group)
                ax.set_xlabel(feature)
                ax.set_ylabel('Frequency')
                ax.set_title('Histogram of '+ feature + ' by ' + outcome)
                ax.legend()
                fig.savefig(path + 'histfrequency_'+feature+'.png')
                return '/images/histfrequency_'+feature+'.png'
            except Exception as e:
                print('feature ' + feature + ' histogram failed.')
                print(e)
        else:
            try:
                fig, ax = plt.subplots(figsize=(10, 10))
                fig = sns.catplot(y=feature, kind="count", hue=outcome, 
                                      palette="pastel", edgecolor=".6", 
                                      #estimator=lambda y: len(y),
                                      data=in_data)
                    
                fig.savefig(path + 'bar_'+feature+'.png')
                return '/images/bar_'+feature+'.png'
            except:
                print('feature ' + feature + ' barplot failed.')
        plt.close('all') 
    pass

def make_summary(feature, outcome, collection, db='raw_data'):
    
    # TODO: Figure out how to query mongo by column rather than getting all the data. That's what 'query' is for right?
    mongo_conn = MongoClient(**mongo_connection_info)
    in_data = mongo_to_df(mongo_conn[db], collection)

    # Get statistics for all observations
    summary_total = pd.DataFrame(columns=['Statistic', 'Total'])
    summary_total.loc[0] = ['observations', len(in_data.index)]
    summary_total.loc[1] = ['non missing', in_data[feature].count()]
    
    if is_numeric_dtype(in_data[feature]):
        summary_total.loc[2] = ['missing', in_data[feature].isnull().sum()]
    else:
        summary_total.loc[2] = ['missing', in_data[feature].isna().sum()]
        
    summary_total.loc[3] = ['unique', in_data[feature].nunique()]        
    summary_total_desc = in_data[feature].describe().to_frame()
    
    # Format dataframe
    summary_total_desc.insert(0, 'Statistic', summary_total_desc.index)
    summary_total_desc.rename({feature: 'Total'}, axis=1, inplace=True)
    
    if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
        all_total = pd.concat([summary_total, summary_total_desc.iloc[1:]], ignore_index=True)
    else:
        all_total = pd.concat([summary_total, summary_total_desc.iloc[2:]], ignore_index=True)
        
    # Get statistics by outcome value
    summary_outcome = in_data.groupby(outcome)[outcome].count().to_frame()
    summary_outcome.rename({outcome: 'observations'}, axis=1, inplace=True)
    
    nm = in_data.groupby([outcome]).agg({feature:['count']})
    nm.columns = ["non missing"]
    summary_outcome = summary_outcome.merge(nm, how='outer', left_index=True, right_index=True)
    
    miss = in_data[feature].isnull().groupby(in_data[outcome]).sum().to_frame()
    miss.columns = ["missing"]
    summary_outcome = summary_outcome.merge(miss, how='outer', left_index=True, right_index=True)

    nu = in_data.groupby([outcome]).agg({feature:['nunique']})
    nu.columns = ["unique"]
    summary_outcome = summary_outcome.merge(nu, how='inner', left_index=True, right_index=True)

    # Format dataframe
    summary_outcome_desc = in_data.groupby(outcome)[feature].describe()
    if is_numeric_dtype(in_data[feature]):
        summary_outcome = summary_outcome.merge(summary_outcome_desc.drop('count',axis=1), how='outer', left_index=True, right_index=True)
    else:
        summary_outcome = summary_outcome.merge(summary_outcome_desc.drop(['count','unique'],axis=1), how='outer', left_index=True, right_index=True)           
    summary_outcome_trans = summary_outcome.transpose()
    new_columns = [outcome + ' = ' + str(list(summary_outcome_trans)[0]), outcome + ' = ' + str(list(summary_outcome_trans)[1])]
    summary_outcome_trans.columns = new_columns
    
    # Merge total and by outcome statistics 
    summary = all_total.merge(summary_outcome_trans, how='outer', left_on='Statistic', right_index=True)
    return __format_dataframe(summary)
        
def make_frequencies(feature, outcome, rows_limit, collection, db="raw_data"):

    # TODO: Figure out how to query mongo by column rather than getting all the data. That's what 'query' is for right?
    mongo_conn = MongoClient(**mongo_connection_info)
    in_data = mongo_to_df(mongo_conn[db], collection)

    if is_numeric_dtype(in_data[feature]):
        if in_data[feature].nunique() < rows_limit:
            vals = in_data.groupby(outcome)[feature].value_counts(ascending=True)
            vals_df = vals.unstack(level=1).transpose()
            vals_df.columns = [outcome + ' = ' + str(col) for col in vals_df.columns]
            vals_df = vals_df.reset_index()
        else:
            bins = np.linspace(math.floor(np.nanmin(in_data[feature])),math.ceil(np.nanmax(in_data[feature])), rows_limit)
            groups = in_data.groupby([outcome, pd.cut(in_data[feature], bins)])
            vals = groups.size().unstack().transpose()
            vals.columns = [outcome + ' = ' + str(col) for col in vals.columns]
            vals_df = vals.reset_index()

        return __format_dataframe(vals_df)
    else:
        vals = in_data.groupby(outcome)[feature].value_counts()
        vals_df = vals.unstack(level=1).transpose()
        vals_df.columns = [outcome + ' = ' + str(col) for col in vals_df.columns]
        vals_df = vals_df.reset_index()
        return __format_dataframe(vals_df[:rows_limit])
        


# INTERNALLY USED FUNCTIONS

# do any necessary formatting of the dataframes here. Right now, this only changes the format to
# {headers: [header1, header2...headerX], rows: [ [val11, val12,...val1X], [val21, val22, ...val2X] ... ]}
# This is easier for iterating over with django templating engine
def __format_dataframe(df):
    df_dict = df[1:].to_dict()
    headers = [key for key in df_dict.keys()]
    rows = [[val[key] for val in df_dict.values()] for key in next(iter(df_dict.values())).keys()]
    return {'headers': headers, 'rows': rows}
