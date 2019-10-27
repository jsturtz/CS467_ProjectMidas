import json, sys, getopt, os
import pandas as pd
import numpy as np


def make_data_dictionary(in_data, out_html_file):

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
    
    # return html file
    return dd[1:].to_html(out_html_file, classes=["table"])

# load sample data
train_transaction = pd.read_csv('./transaction_small.csv')
train_id = pd.read_csv('identity_small.csv')
    
# generate data dictionary
make_data_dictionary(train_transaction, 'data_dictionary_transaction.html')
make_data_dictionary(train_id, 'data_dictionary_id.html')
