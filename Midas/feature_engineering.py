# methods to perform feature engineering on df
import featuretools as ft
from featuretools.primitives import make_trans_primitive
from featuretools.variable_types import Boolean, Categorical
from nlp_primitives import (
    DiversityScore,
    LSA,
    MeanCharactersPerWord,
    PartOfSpeechCount,
    PolarityScore,
    PunctuationCount,
    StopwordCount,
    TitleWordCount,
    UniversalSentenceEncoder,
    UpperCaseCount,
)

import pandas as pd
import numpy as np


pd.options.mode.use_inf_as_na = True


# add column to present vs non_present values - (PRESENT)foo
def value_present(value):
    return pd.isna(value)


def feature_synthesis(target, es):
    # use feature synthesis to generate features
    # standard array primitives, along with present

    # custom primitives
    # in theory, we could use primitives for multiple input types
    # but attempts to use this feature and the examples in documentation
    # don't seem to work.
    CatPresent = make_trans_primitive(
        function=value_present,
        input_types=[Categorical],
        return_type=Boolean,
        name="CATEGORY_PRESENT",
        description="checks that there is a value in the column",
    )

    agg_defaults = [
        "sum",
        "std",
        "max",
        "skew",
        "min",
        "mean",
        "count",
        "percent_true",
        "num_unique",
        "mode",
    ]
    trans_defaults = [
        "day",
        "year",
        "month",
        "weekday",
        "haversine",
        "num_words",
        "num_characters",
        CatPresent,
        DiversityScore,  # start of nlp_primitives
        LSA,
        MeanCharactersPerWord,
        PartOfSpeechCount,
        PolarityScore,
        PunctuationCount,
        StopwordCount,
        TitleWordCount,
        UniversalSentenceEncoder,
        UpperCaseCount,
    ]

    feature_matrix, feature_defs = ft.dfs(
        entityset=es,
        target_entity=target,
        agg_primitives=agg_defaults,
        trans_primitives=trans_defaults,
    )

    return feature_matrix, feature_defs


def create_entityset(_id, entities, relationships=[]):
    """
    _id - name of the entityset, usually the focus
    entities - [{'df': df, '_id': unique_id,
                'index_col': index_col_name, 'time_index': time_index}]
    relationships - [{'parent_id': abc, 'parent_rel_col': abc_id,
                     'child_id': bcd, 'child_rel_col': bcd_id}]
    """
    es = ft.EntitySet(_id)
    for entity in entities:
        es.entity_from_dataframe(dataframe=entity["df"], entity_id=entity["name"])
        set_entity_var_types(es[entity["name"]], entity["var_type_mapping"])

    for rel in relationships:
        es.add_relationship(
            ft.Relationship(
                es[rel["parent_id"]][rel["parent_var"]],
                es[rel["child_id"]][rel["child_var"]],
            )
        )

    return es


def convert_df_types(df):
    """Convert pandas data types for memory reduction."""

    # Iterate through each column
    for c in df:
        # Convert objects to category
        if (df[c].dtype == "object") and (df[c].nunique() < df.shape[0]):
            df[c] = df[c].astype("category")

        # Booleans mapped to integers
        elif set(df[c].unique()) == {0, 1}:
            df[c] = df[c].astype(bool)

        # Float64 to float32
        elif df[c].dtype == float:
            df[c] = df[c].astype(np.float32)

        # Int64 to int32
        elif df[c].dtype == int:
            df[c] = df[c].astype(np.int32)

    return df


def set_entity_var_types(entity, col_mapping):
    """
    entity - entity
    col_mapping - {
        "Datetime": ["created_at", "booked_at"],
        "Categorical": ["vin", "rfid"],
        "Numeric": ["parking_fee"]
    }
    """
    # for full list of variable types:
    # https://docs.featuretools.com/en/stable/api_reference.html#variable-types
    for _type, var_list in col_mapping.items():
        for var in var_list:
            try:
                entity.convert_variable_type(
                    var, getattr(ft.variable_types.variable, _type)
                )
            except Exception:
                # if we can't convert the data, just change the type anyway
                entity.convert_variable_type(
                    var, getattr(ft.variable_types.variable, _type, convert_data=False)
                )
