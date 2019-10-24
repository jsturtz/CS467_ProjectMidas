import json, sys, getopt, os
import pandas as pd
import numpy as np


def make_data_dictionary(in_df, out_html_file):

    # create a new dataframe for the data dictionary containing the feature list
    dd = pd.DataFrame(list(dfname),columns=['Feature'])
    
    #  add variable type to the data dictionary
    dd['Type'] = dfname.dtypes.tolist()
    
    # add count of distinct values to data dictionary
    dd['Distinct'] = dfname.nunique().tolist()
    
    # make lists for frequency counts and missing values
    freq_counts = []
    missing_counts = []
    
    # iterate through the columns
    for column in dfname:
        # get frequency counts
        vcs = dfname[column].value_counts(dropna=False).to_dict()
        
        # use binning if the feature is numeric and there are many unique values
        if len(vcs) > 10 and np.issubdtype(dfname[column].dtype,np.number):
            bins_data = dfname[column].value_counts(dropna=False, bins = 10)
            freq_counts.extend([(bins_data.to_dict())])
            
        # if many unique values, but categorical variable, only keep top 10 frequencies
        elif len(vcs) > 10:
            freq_counts.extend([dfname[column].value_counts(dropna=False)[:10].to_dict()])
        
        # for a small number of unique values, keep all frequencies
        else:
            freq_counts.extend([vcs])
            
        # obtain count of missing values    
        if np.issubdtype(dfname[column].dtype,np.number):
            # for numeric variables, use isnull
            missing_counts.extend([dfname[column].isnull().sum()])
        else:
            missing_counts.extend([dfname[column].isna().sum()])
            #missing_counts.extend([(dfname[column].values == '').sum()])
    
    # add count of missing values
    dd['Missing'] = missing_counts
        
    # Add minimum value for each feature (if applicable)
    dd = dd.merge(dfname.min().to_frame(), left_on=['Feature'], right_index=True, how='left')
    dd.rename(columns={dd.columns[-1]: 'Minimum'}, inplace=True)
    
    # Add maximum value for each feature (if applicable)
    dd= dd.merge(dfname.max().to_frame(), left_on=['Feature'], right_index=True, how='left')
    dd.rename(columns={dd.columns[-1]: 'Maximum'}, inplace=True)
        
    dd['Top Frequencies'] = freq_counts

    # set options so columns aren't truncated
    pd.set_option('display.max_colwidth', -1)
    
    # return html file
    return dd[1:].to_html(out_html_file)

# load sample data
#train_transaction = dd.read_csv('train_transaction.csv')
#train_id = dd.read_csv('train_identity.csv')
    
# generate data dictionary
#make_data_dictionary(train_transaction, 'data_dictionary_transaction.html')
#make_data_dictionary(train_id, 'data_dictionary_transaction.html')
