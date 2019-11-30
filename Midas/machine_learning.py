# template code to train models
from Midas.databases import (
    postgres_to_df,
    save_model,
    get_model
)
from Midas.ML_pipeline import ML_Custom
from Midas.data_cleaning import clean_data

import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train_linear_model(x_train, y_train, x_test, y_test, model=LogisticRegression, **kwargs):
    # fit data
    linear_model = model().fit(x_train, y_train, **kwargs)
    score = model.score(x_test, y_test)
    return linear_model, score


def format_model_results(results):
    return {
        "algorithm": [results["algorithm"]],
        "cv_mean_auc": [results["cv_mean_auc"]],
        "confusion_matrix_tn": [results["confusion_matrix"]["tn"]],
        "confusion_matrix_tp": [results["confusion_matrix"]["tp"]],
        "confusion_matrix_fn": [results["confusion_matrix"]["fn"]],
        "confusion_matrix_fp": [results["confusion_matrix"]["fp"]],
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
    X = df.drop(label)
    return train_test_split(X, y, test_size=split_percent)


def train_model(dataset_id, label, model_strategy="KNN", **kwargs):
    # retrieve data from db
    df = retrieve_data(dataset_id)
    x_train, x_test, y_train, y_test = split_dataset(df, label)

    results, trained_model = ML_Custom(model_strategy).fit(x_train, y_train)
    # save model results
    results = format_model_results(results)
    model_id = save_model(trained_model, dataset_id, model_strategy, results)
    # return results to caller
    return model_id, results


def run_model(dataset_id, model_id, label_mapping, **cleaning_configs):
    # we should store the label mapping that corresponds
    # to the dataset somewhere, so we don't have to ask to user to load it
    df = retrieve_data(dataset_id)
    # get the cleaning method and apply to dataset
    df = clean_data(model_id, label_mapping, **cleaning_configs)

    # unpickle the model and load the model
    model_data = get_model({"model_id": model_id})
    model = pickle.load(model_data["model"])
    # run model against the df
    results = model.predict(df)
    return results
