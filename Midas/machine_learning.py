# template code to train models
from Midas.databases import (
    postgres_to_df,
    save_model,
    get_model
)
from Midas.ML_pipeline import ML_Custom, categorical_to_dummy
from Midas.data_cleaning import clean_data

import pickle
import codecs
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train_linear_model(x_train, y_train, x_test, y_test, model=LogisticRegression, **kwargs):
    # fit data
    linear_model = model().fit(x_train, y_train, **kwargs)
    score = model.score(x_test, y_test)
    return linear_model, score


def format_model_results(results):
    return {
        "algorithm": results["algorithm"],
        "cv_mean_auc": float(results["cv_mean_auc"]),
        "confusion_matrix_tn": int(results["confusion_matrix"]["tn"]),
        "confusion_matrix_tp": int(results["confusion_matrix"]["tp"]),
        "confusion_matrix_fn": int(results["confusion_matrix"]["fn"]),
        "confusion_matrix_fp": int(results["confusion_matrix"]["fp"]),
    }


def retrieve_data(dataset_id, **kwargs):
    """
    allows option for user to specify datetime cols
    """
    query = query_builder(dataset_id)

    # does not necessarily handle datetime data right now
    # would require user input or some metadata config
    # but kaggle dataset doesn't have datetime data
    return postgres_to_df(query, **kwargs)


def query_builder(dataset_id):
    # all columns for now
    # can add customization later
    # most customization of dataset should be coming from feature selection
    SELECT = """
             select *
             from {dataset_id}
             """.format(
        dataset_id=dataset_id
    )
    return SELECT


def split_dataset(df, label, split_percent=0.70):
    y = df[label]
    X = df.drop(label, axis="columns")
    return train_test_split(X, y, test_size=split_percent)


def train_model(df, label, model_strategy="KNN", **kwargs):
    df = categorical_to_dummy(df, label)
    x_train, x_test, y_train, y_test = split_dataset(df, label)
    results, trained_model = ML_Custom(model_strategy).fit(x_train, y_train)
    # save model results
    results = format_model_results(results)
    pickled_model = codecs.encode(pickle.dumps(trained_model), "base64").decode()
    return pickled_model, results


def run_model(df, label, model):
    # unpickle the model and load the model
    df = categorical_to_dummy(df, label)
    model = pickle.loads(codecs.decode(model.encode(), "base64"))
    # run model against the df
    print(f"model: {model}")
    results = model.predict(df)
    return results
