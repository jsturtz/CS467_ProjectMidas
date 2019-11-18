import pandas as pd
from sklearn.preprocessing import LabelEncoder


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