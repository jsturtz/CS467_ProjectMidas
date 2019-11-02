import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
import matplotlib as mpl

mpl.use('Agg')

def make_univariate_plots(in_data, outcome, rows_limit):
    features = list(in_data)
    for feature in features:
        if feature != outcome:
            make_plot(in_data, feature, outcome, rows_limit)
        
def make_plot(in_data, feature, outcome, rows_limit):
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
                fig.savefig('histfrequency_'+feature+'.png')
            except:
                print('feature ' + feature + ' histogram failed.')
        else:
            try:
                fig, ax = plt.subplots(figsize=(10, 10))
                fig = sns.catplot(y=feature, kind="count", hue=outcome, 
                                      palette="pastel", edgecolor=".6", 
                                      #estimator=lambda y: len(y),
                                      data=in_data)
                    
                fig.savefig('bar_'+feature+'.png')
            except:
                print('feature ' + feature + ' barplot failed.')
        plt.close('all') 


# load sample data
#train_transaction = pd.read_csv('transaction_small.csv', index_col=0)
#train_id = pd.read_csv('identity_small.csv', index_col=0)
train_transaction = pd.read_csv('train_transaction.csv', index_col=0)
train_id = pd.read_csv('train_identity.csv', index_col=0)

in_df = train_transaction.merge(train_id, how='inner', left_on='TransactionID', right_on='TransactionID')

make_univariate_plots(in_df, 'isFraud', 25)


#train_transaction.iloc[:,0:10]

"""
                fig, ax = plt.subplots(figsize=(10, 10))
                for group in in_data[outcome].unique():
                    sns.distplot((in_data.dropna(subset=[feature])).loc[in_data[outcome] == group, feature],
                                     kde=True, ax=ax, label=group)
                ax.set_xlabel(feature)
                ax.set_ylabel('Density')
                ax.set_title('Histogram of '+ feature + ' by ' + outcome)
                ax.legend()
                fig.savefig('histdensity_'+feature+'.png')
"""

