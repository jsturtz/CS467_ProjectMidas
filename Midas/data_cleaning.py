from Midas.databases import mongo_to_df, load_df_to_postgres, MongoInterface
from Midas.configs import default_db, raw_data_collection

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn import preprocessing
from sklearn.decomposition import PCA


def remove_row_with_missing(df):
    return df.dropna()


def remove_col_with_no_data(df):
    to_drop = []
    for col in df.columns:
        # determine if column is entirely "True" values
        if df[col].all(axis=None):
            to_drop.append(col)
        # determine if there's only 1 unique value
        elif df[col].nunique() == 1:
            to_drop.append(col)

    return df.drop(to_drop, axis="columns")


def impute_numeric(series, strategy):
    print("imputing numeric")
    def _impute_to_mean(series):
        return series.fillna(value=series.mean())

    def _impute_to_median(series):
        return series.fillna(value=series.median())

    if strategy == "mean":
        return _impute_to_mean(series)
    elif strategy == "median":
        return _impute_to_median(series)
    else:
        return None


def impute_categorical(series, strategy):
    print("imputing categorical")
    def _impute_to_missing(series):
        return series.fillna(value="missing")

    if strategy == "fill_with_missing":
        return _impute_to_missing(series)
    else:
        return None


def imputation(df, label_mapping, numeric_strategy, categorical_strategy):
    if label_mapping:
        for col in df.columns:
            if col in label_mapping["numeric"]:
                print("imputing")
                df[col] = impute_numeric(df[col], numeric_strategy)
            elif col in label_mapping["categorical"]:
                df[col] = impute_categorical(df[col], categorical_strategy)
    return df


def clean_training_data(filepath, standardize, outliers, variance_retained, label_mapping, numeric_strategy, categorical_strategy):
    df = pd.read_csv(filepath)

    if not numeric_strategy:
        numeric_strategy = "mean"
    if not categorical_strategy:
        categorical_strategy = "fill_with_missing"

    print(numeric_strategy)
    print(categorical_strategy)

    return clean_data(df, label_mapping, numeric_strategy, categorical_strategy, outliers, standardize, variance_retained)

def clean_data(
    df,
    label_mapping,
    # numeric_strategy="mean",
    # categorical_strategy="fill_with_missing",
    numeric_strategy,
    categorical_strategy,
    outliers=None,
    standardize=None,
    variance_retained=0,
):

    # cleaning process
    df = remove_col_with_no_data(df)

    df = remove_outliers(df, outliers)

    df = standardize_numeric_features(df, standardize)

    df = imputation(df, label_mapping, numeric_strategy, categorical_strategy)

    # this step breaks the data cleaning process
    # df = dimensionality_reduction_using_PCA(df, variance_retained)

    return df


# Removes outliers in numeric features outside of (Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
# When argument outliers is set to 'obs', the entire row (observation) is removed
# When argument 'outliers is set to 'value', the outlier value is recoded to missing

# Use: outliers = None obs value
def remove_outliers(in_df, outliers):
    in_data = in_df.copy()
    if outliers:
        features = list(in_data)
        for feature in features:
            if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
                # get bounds
                sorted_feature = sorted(in_data[feature])
                q1, q3 = np.percentile(sorted_feature, [25, 75])
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                if (outliers) == "obs":
                    in_data.drop(
                        in_data[in_data[feature] < lower_bound].index, inplace=True
                    )
                    in_data.drop(
                        in_data[in_data[feature] > upper_bound].index, inplace=True
                    )
                elif (outliers) == "value":
                    in_data.loc[in_data[feature] < lower_bound, feature] = np.nan
                    in_data.loc[in_data[feature] > upper_bound, feature] = np.nan
    return in_data


# Standardizes all numeric features such that each feature mean = 0 and variance = 1
def standardize_numeric_features(in_df, standardize):
    in_data = in_df.copy()
    if standardize:
        features = list(in_data)
        scaler = preprocessing.StandardScaler()
        for feature in features:
            if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
                in_data[feature] = scaler.fit_transform(in_data[feature].to_frame())
    return in_data


# Uses PCA to reduce the dimensionality of the numeric features.  The original
# numeric features are dropped and replaced by a set of new principal components
# The number of components selected are the minimum needed to ensure that
# at least x 'variance explained' is retained.  In other words, 30 components might be
# required to ensure that .95 of the variance in the original set of 100 features is
# retained
# NOTE: PCA requires imputed data (no missing)

# Use: variance_retained = .95.  0 means don't use PCA.  use original.

# FIXME-Ellen:
# getting error -> Midas/data_cleaning.py:162:17: F821 undefined name 'nonpca_features_df'
def dimensionality_reduction_using_PCA(in_df, variance_retained):
    in_data = in_df.copy()
    if variance_retained > 0:
        features = list(in_data)
        scaler = preprocessing.StandardScaler()
        pca = PCA(variance_retained)
        pca_df = pd.DataFrame(index=in_data.index)
        for feature in features:
            if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
                pca_df[feature] = scaler.fit_transform(in_data[feature].to_frame())
            else:
                nonpca_features_df[feature] = in_data[feature]
        pca.fit(pca_df)
        pca_df = pca.transform(pca_df)
        print("number of components = ", pca.n_components_)
        return pd.concat([nonpca_features_df, pca_df], axis=1)
    else:
        return in_data


# def suggest_dtypes(collection, db="raw_data"):

#     mongo_conn = MongoClient(**mongo_connection_info)
#     df = mongo_to_df(mongo_conn[db], collection)
#     # Do analysis here to suggest type labels for features
#     return {

#     }


""" TESTING

train_transaction = pd.read_csv('train_transaction.csv', index_col=0)
train_id = pd.read_csv('train_identity.csv', index_col=0)
in_df = train_transaction.merge(
    train_id, how='left', left_on='TransactionID', right_on='TransactionID')


#a = remove_outliers(in_df,'obs')
#b = remove_outliers(in_df,'values')
#c = standardize_numeric_features(in_df)
#d = dimensionality_reduction_using_PCA(in_df, .95)

# initialize list of lists
data = [[3, 10, 5],
        [5, 15, 6],
        [2, 99, 3],
        [3, 11, 4],
        [3, 13, 3],
        [5, 14, 5],
        [3, 10, 5],
        [-10, 15, 6],
        [2, 14, 3],
        [3, 11, 4],
        [3, 13, 3],
        [5, 14, 5]
        ]

# Create the pandas DataFrame
df = pd.DataFrame(data, columns = ['a', 'b', 'c'])

remove_outliers(df, 'obs')

standardize_numeric_features(df)

dimensionality_reduction_using_PCA(df, .95)
"""
