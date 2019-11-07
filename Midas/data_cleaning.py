import pandas as pd


def remove_row_with_missing(df):
    return df.dropna()


def remove_col_with_no_data(df):
    to_drop = []
    for col in df.columns:
        if df[col].all(axis='columns'):
            to_drop.append(col)
    return df.drop(to_drop, axis='columns')


def impute_numeric(series, strategy):

    def _impute_to_mean(series):
        return series.fillna(value=series.mean())

    def _impute_to_median(series):
        return series.fillna(value=series.median())

    if strategy == 'mean':
        return _impute_to_mean(series)
    elif strategy == 'median':
        return _impute_to_median(series)
    else:
        return None


def impute_categorical(series, strategy):

    def _impute_to_missing(series):
        return series.fillna(value='missing')

    if strategy == 'fill_with_missing':
        return _impute_to_missing(series)
    else:
        return None


def imputation(
        df,
        label_mapping,
        numeric_strategy='mean',
        categorical_strategy='fill_with_missing'):
    for col in df.columns:
        if col in label_mapping['numeric']:
            df[col] = impute_numeric(df[col], numeric_strategy)
        elif col in label_mapping['categorical']:
            df[col] = impute_categorical(df[col], categorical_strategy)
    return df
