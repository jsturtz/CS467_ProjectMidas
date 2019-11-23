# template code to train models
from Midas.databases import postgres_to_df, load_df_to_postgres
from Midas.ml_pipeline import ML_Custom

import pandas as pd
import pickle
from hashlib import md5
import time

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train_linear_model(x_train, y_train, model=LogisticRegression, **kwargs):
    # fit data
    linear_model = model().fit(x_train, y_train, **kwargs)
    score = model.score(x_test, y_test)
    return linear_model, score


def save_model(model):
    # save in datastores/models for now
    pickled_model = pickle.dumps(model)
    model_id = f'{md5(pickled_model.encode()).hexdigest()}_{int(time.time())}'

    with open(f'datastores/models/{model_id}', 'w') as ofp:
        ofp.write(pickled_model)

    return model_id


def record_model_results(dataset_id, model_id, results):
    df = pd.DataFrame(
        {
        'dataset_id': dataset_id,
        'model_id': [model_id],
        'algorithm': [results['algorithm']],
        'cv_mean_auc': [results['cv_mean_auc']],
        'confusion_matrix_tn': [model_results["confusion_matrix"]["tn"]],
        'confusion_matrix_tp': [model_results["confusion_matrix"]["tp"]],
        'confusion_matrix_fn': [model_results["confusion_matrix"]["fn"]],
        'confusion_matrix_fp': [model_results["confusion_matrix"]["fp"]],
        }
    )
    load_df_to_postgres(df, 'model_results', if_exists='append')


def retrieve_data(dataset_id, **kwargs):
    '''
    allows option for user to specify datetime cols
    '''
    query = query_builder(dataset_id)

    # does not necessarily handle datetime data right now
    # would require user input or some metadata config
    # but kaggle dataset doesn't have datetime data
    return postgres_to_df(query, **kwargs)


def query_builder(dataset_id):
    # all columns for now
    # can add customization later
    # most customization of dataset should be coming from feature selection
    SELECT = '''
             select *
             from {dataset_id}
             '''.format(dataset_id=dataset_id)
    return SELECT


def split_dataset(df, label, split_percent=.70):
    y = df[label]
    X = df.drop(label)
    return train_test_split(X, y, test_size=split_percent)


def train_model(dataset_id, label,
                model_strategy='KNN', **kwargs):
    # retrieve data from db
    df = retrieve_data(dataset_id)
    x_train, x_test, y_train, y_test = split_dataset(df, label)

    results, trained_model = ML_Custom(model_strategy).fit(x_train, y_train)

    # save model results
    model_id = save_model(trained_model)
    record_model_results(dataset_id, model_id, results)
