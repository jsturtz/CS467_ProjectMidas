# template code to train models
from Midas.databases import postgres_to_df, upsert

import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train_linear_model(df, label, model=LogisticRegression, **kwargs):
    # split dataset
    x_train, x_test, y_train, y_test = split_dataset(df, label)
    # fit data
    linear_model = model().fit(x_train, y_train, **kwargs)
    return linear_model


def save_model(_id, model):
    # save in datastores/models for now
    with open(f'datastores/models/{_id}', 'w') as ofp:
        pickle.dump(model, ofp)


def record_model_results(_id, model, x, y):
    # get score and save record to database
    # _id as index
    score = model.score(x, y)
    df = pd.DataFrame({'_id': [_id], 'score': [score])
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
