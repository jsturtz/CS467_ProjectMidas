from ast import literal_eval
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer


def categorical_encoder(col, ordered=True):
    # takes categorical data and encodes to n-1 values
    # returns encoded dataset and encoder mapping for storage
    # by default, provides the label as ordered values
    enc = LabelEncoder()

    if ordered:
        enc.classes_ = col.value_counts().index
        encoded = enc.transform(col)
    else:
        encoded = enc.fit_transform(col)

    return pd.Series(encoded), pd.Series(enc.classes_)


def variable_length_list_onehot_encoding(col):
    """
    args:
        col - series with values as strings that look like python lists

    this is for handling weird list-like columns
    like vehicle_group_ids
    or other columns that represent the one-many relationship of an object
    output dataframe of {col_name}_option1
    """

    # create a set of labels from the data set
    col_as_df = col.apply(literal_eval).apply(pd.Series)
    encoding_set = list(set(col_as_df.stack().value_counts().index))
    mlb = MultiLabelBinarizer(encoding_set)
    matrix = [tuple(x) for x in col_as_df.to_records(index=False)]
    mlb_df = mlb.fit_transform(matrix)
    onehot_labels = [f"{col.name}_has_{x}" for x in mlb.classes]
    return pd.DataFrame(data=mlb_df, columns=onehot_labels)
