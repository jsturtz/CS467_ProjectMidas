
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
import matplotlib as mpl
from scipy import stats
from sklearn.linear_model import LogisticRegression 
from sklearn.model_selection import train_test_split

mpl.use('Agg')

"""
This is a tool to assist in the preprocessing / data exploration phase.
Impact and pvalues can help users identify and analyze predictive relationships
between individual features and the outcome variable.

This can be useful for prioritizing areas of focus/investigation and potentially
for data cleaning / data recoding purposes.  Patterns highlighted in this analysis
may inform subsequent data recoding actions.

Note that multiple hypothesis tests are associated with type I error (false positives)
so these tests should be viewed more as an aid for investigation/analysis rather than
a conclusive test for the relationship betweeen each predictor and outcome.
"""


# Gets an impact score (0-100) for each feature.  Prints to stdout by feature type
def get_impact(in_data, outcome, rows_limit, pValue):
    features = list(in_data)
    numeric_dict = {}
    categorical_dict = {}
    for feature in features:
        if feature != outcome:
            if is_numeric_dtype(in_data[feature]):
                pass
                numeric_dict[feature] = numeric_impact(in_data, feature, outcome)
            else:
                categorical_dict[feature] = categorical_impact(in_data, feature, outcome, rows_limit, pValue)
    n_sorted_keys = sorted(numeric_dict, key=numeric_dict.get, reverse=True)
    print("Numeric features results:")
    for r in n_sorted_keys:
        if numeric_dict[r] > 0:
            print(r, numeric_dict[r])
    c_sorted_keys = sorted(categorical_dict, key=categorical_dict.get, reverse=True)
    print()
    print("Categorical features results:")
    for r in c_sorted_keys:
        if categorical_dict[r] > 0:
            print(r, categorical_dict[r])

# uses linear regression to predict the outcome from each feature individually
def numeric_impact(in_data, feature, outcome):
    # Split X and y into X_
    s = pd.Series(in_data[feature].notna(), name='bools')
    noMissY = in_data[outcome][s]
    noMissX = in_data[feature][s]
    if len(noMissX) > 0:
        X_train, X_test, y_train, y_test = train_test_split(noMissX.values.reshape(-1,1), noMissY, test_size=0.30, random_state=1)
        classifier = LogisticRegression(random_state = 0) 
        classifier.fit(X_train, y_train) 
        predictions = classifier.predict(X_test)
        impact = ((sum(predictions == y_test))/.3)
    else:
        impact = 0
    return round(100 * impact / len(in_data))

# uses a binomial test to test the relationship between each categorical value and the outcome variable
def categorical_impact(in_data, feature, outcome, rows_limit, pValue):
    vals = in_data.groupby(outcome)[feature].value_counts()
    vals_df = vals.unstack(level=1).transpose()

    miss = in_data[feature].isna().groupby(in_data[outcome]).sum().to_frame().transpose()   
    miss.index.values[0] = 'Missing'

    vals_with_miss = pd.concat([vals_df,miss],ignore_index=False)


    vals_with_miss[np.isnan(vals_with_miss)] = 0
    vals_with_miss.columns = [outcome + ' = ' + str(col) for col in vals_with_miss.columns]
    vals_with_miss = vals_with_miss.reset_index()

    p_isFraud = sum(vals_with_miss["isFraud = 1"]) / (sum(vals_with_miss["isFraud = 0"]) + sum(vals_with_miss["isFraud = 1"]))
    
    vals_with_miss["Prop_Observed"] = vals_with_miss["isFraud = 1"] / (vals_with_miss["isFraud = 0"] + vals_with_miss["isFraud = 1"])
    
    vals_with_miss["Prop_Expected"] = p_isFraud

    vals_with_miss["P_Value"] = vals_with_miss.apply(calculate_binom, p_isFraud = p_isFraud,axis=1)

    np.any(vals_with_miss["P_Value"] < pValue)

    sorted_df = vals_with_miss.sort_values(by=['Prop_Observed', 'index'])

    sorted_df["Obs_Impacted"] = sorted_df.apply(observations_affected, axis=1)
    
    sorted_df[:rows_limit].to_html('impact '+feature+'.html', index=False)  
    
    return round(100 * sum(sorted_df["Obs_Impacted"]) / len(in_data))

def observations_affected(row):
    return row["isFraud = 1"] + row["isFraud = 0"] if row["P_Value"] < pValue else 0
    
def calculate_binom(row, p_isFraud):
    return stats.binom_test(row["isFraud = 1"], n=(row["isFraud = 0"] + row["isFraud = 1"]), p=p_isFraud, alternative='two-sided')

# load sample data
#train_transaction = pd.read_csv('transaction_small.csv', index_col=0)
#train_id = pd.read_csv('identity_small.csv', index_col=0)
train_transaction = pd.read_csv('train_transaction.csv', index_col=0)
train_id = pd.read_csv('train_identity.csv', index_col=0)
in_df = train_transaction.merge(train_id, how='inner', left_on='TransactionID', right_on='TransactionID')

### set constants

outcome = "isFraud"
pValue = .01 
rows_limit = 300

# run impact
get_impact(in_df, outcome, rows_limit, pValue)