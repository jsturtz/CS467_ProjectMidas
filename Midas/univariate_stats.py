import pandas as pd
import numpy as np
import math
from pandas.api.types import is_numeric_dtype
import matplotlib as mpl

mpl.use('Agg')


def make_univariate_stats(in_data, outcome, rows_limit):
    features = list(in_data)
    for feature in features:
        if feature != outcome:
            make_summary(in_data, feature, outcome)
            make_frequencies(in_data, feature, outcome, rows_limit)
        
def make_summary(in_data, feature, outcome):
    
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
 
        try:
            summary.to_html('summary '+feature+'.html', index=False, float_format=lambda x: '%10.2f' % x)
        except:
            print(summary)
        
def make_frequencies(in_data, feature, outcome, rows_limit):
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
        vals_df.to_html('frequencies '+feature+'.html', index=False) 
    else:
        vals = in_data.groupby(outcome)[feature].value_counts()
        vals_df = vals.unstack(level=1).transpose()
        vals_df.columns = [outcome + ' = ' + str(col) for col in vals_df.columns]
        vals_df = vals_df.reset_index()
        vals_df[:rows_limit].to_html('frequencies '+feature+'.html', index=False)   
        

# load sample data
#train_transaction = pd.read_csv('transaction_small.csv', index_col=0)
#train_id = pd.read_csv('identity_small.csv', index_col=0)
train_transaction = pd.read_csv('train_transaction.csv', index_col=0)
train_id = pd.read_csv('train_identity.csv', index_col=0)
        
in_df = train_transaction.merge(train_id, how='inner', left_on='TransactionID', right_on='TransactionID')

make_univariate_stats(in_df, 'isFraud', 25)



#train_transaction.iloc[:,0:10]


