#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Created on Wed Nov 13 18:03:05 2019
References:
    https://www.kdnuggets.com/2017/03/simple-xgboost-tutorial-iris-dataset.html
    https://towardsdatascience.com/support-vector-machine-python-example-d67d9b63f1c8
    https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html
    https://www.datacamp.com/community/tutorials/adaboost-classifier-python
    https://www.datacamp.com/community/tutorials/random-forests-classifier-python
    https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html
    https://www.ritchieng.com/machine-learning-k-nearest-neighbors-knn/
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html#sklearn.metrics.roc_auc_score
    https://scikit-learn.org/stable/auto_examples/svm/plot_svm_kernels.html
@author: ellenscheib
"""

import pandas as pd
import numpy as np
import random
from pandas.api.types import is_numeric_dtype
from sklearn.impute import SimpleImputer
from sklearn import preprocessing
from sklearn.model_selection import KFold
from sklearn.neighbors import KNeighborsClassifier
from statistics import stdev
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.preprocessing import LabelEncoder

# import xgboost as xgb


class ML_Custom:
    def __init__(self, training_method):
        self.seed = random.seed()
        if training_method == "KNN":
            self.model = KNN_training
            self.required_cleaning_options = {
                "standardize": False,
                "missing_data": True,
                "encoding": True,
                "outliers": False,
            }
        elif training_method == "ADA":
            self.model = ADA_training
            self.required_cleaning_options = {
                "standardize": False,
                "missing_data": True,
                "encoding": True,
                "outliers": False,
            }
        elif training_method == "RF":
            self.model = RF_training
            self.required_cleaning_options = {
                "standardize": False,
                "missing_data": True,
                "encoding": True,
                "outliers": False,
            }
        elif training_method == "SVM":
            self.model = SVM_training
            self.required_cleaning_options = {
                "standardize": False,
                "missing_data": True,
                "encoding": True,
                "outliers": False,
            }
        else:
            raise Exception("Not a supported model type")

    def fit(self, x_train, y_train, CV_folds=10):
        return self.model(x_train, y_train, CV_folds, self.seed)

    # returns a dictionary showing the data-cleaning cleaning_options for execution of model
    def get_options(self):
        return self.required_cleaning_options


## KNN = K NEAREST NEIGHBORS
## Fits the KNN model and uses CV to select K (# of neighbors)
## Note: standarizing recommended
## Note: requires dummy coding
## Note: cannot tolerate missing values (imputation or deletion required)
def KNN_training(X_train, y_train, CV_folds, seed):
    # use kfold cross validation
    kf = KFold(n_splits=CV_folds, random_state=seed, shuffle=True)

    # try a range of values of "k" neighbors (1,3,5...25)
    k_range = range(1, 25, 2)

    # Save cross validation results
    results_dict = {}

    # Measure performance for each value of K neigbors across the CV folds
    for k in k_range:
        results_dict[k] = []

    for train_index, cv_index in kf.split(X_train):
        for k in k_range:
            KNNmodel = KNeighborsClassifier(n_neighbors=k)
            KNNmodel.fit(X_train.iloc[train_index], y_train.iloc[train_index])
            predicted = KNNmodel.predict_proba(X_train.iloc[cv_index])[:, 1]
            true_labels = y_train.iloc[cv_index]
            # using area under the curve as the metric since this was used in the competition
            try:
                results_dict[k].append(roc_auc_score(true_labels, predicted))
            except:
                pass

    # The one Standard Error rule: choose the simplest
    # model with CV error no more than one SE above lowest CV error
    # to implement a variant, selecting the simplest model within 1 SE of the best roc_auc_score
    scores = []
    for key in sorted(results_dict):
        if len(results_dict[key]) > 0:
            scores.append(sum(results_dict[key]) / len(results_dict[key]))

    one_SE_rule = max(scores) - stdev(scores)

    found = 0
    for key in sorted(results_dict):
        if (sum(results_dict[key]) / len(results_dict[key])) > one_SE_rule:
            if found == 0:
                selected_k = key  # this is the selected number of neighbors
                cv_mean_auc = sum(results_dict[key]) / len(results_dict[key])
            found = 1

    # store the confusion matrix results for the selected k using the CV data
    model_results = {}
    model_results["algorithm"] = "KNN"
    model_results["cv_mean_auc"] = cv_mean_auc
    model_results["parameters"] = {"K": selected_k}
    model_results["confusion_matrix"] = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}

    for train_index, cv_index in kf.split(X_train):
        KNNmodel = KNeighborsClassifier(n_neighbors=selected_k)
        KNNmodel.fit(X_train.iloc[train_index], y_train.iloc[train_index])
        predicted = KNNmodel.predict(X_train.iloc[cv_index])
        true_labels = y_train.iloc[cv_index]

        # True Positive (TP): we predict a label of 1 (positive), and the true label is 1.
        model_results["confusion_matrix"]["tp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 1)
        )

        # True Negative (TN): we predict a label of 0 (negative), and the true label is 0.
        model_results["confusion_matrix"]["tn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 0)
        )

        # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
        model_results["confusion_matrix"]["fp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 0)
        )

        # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
        model_results["confusion_matrix"]["fn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 1)
        )

    # fit the entire training data to the selected model for use with the test data
    KNNmodel = KNeighborsClassifier(n_neighbors=selected_k)
    KNNmodel.fit(X_train, y_train)

    # model_results["model"] = KNNmodel

    return model_results, KNNmodel


## ADAboost
## Note: standarizing not needed
## Note: requires dummy coding
## Note: cannot tolerate missing values (imputation or deletion required)
def ADA_training(X_train, y_train, CV_folds, seed):

    # use kfold cross validation
    kf = KFold(n_splits=CV_folds, random_state=seed, shuffle=True)

    # try a range of learning rates
    l_range = [1, 0.1, 0.01, 0.001]

    # Save cross validation results
    results_dict = {}

    # Measure performance for each parameter value across the CV folds
    for l in l_range:
        results_dict[l] = []

    for train_index, cv_index in kf.split(X_train):
        for l in l_range:
            # Create adaboost classifer object
            abc = AdaBoostClassifier(n_estimators=50, learning_rate=l)
            # Train Adaboost Classifer
            model = abc.fit(X_train.iloc[train_index], y_train.iloc[train_index])
            # Predict the response for test dataset
            predicted = model.predict_proba(X_train.iloc[cv_index])[:, 1]
            true_labels = y_train.iloc[cv_index]

            # using area under the curve as the metric since this was used in the competition
            try:
                results_dict[l].append(roc_auc_score(true_labels, predicted))
            except:
                pass

    # find the learning rate associated with the highest auc
    scores = {}
    for key in sorted(results_dict):
        if len(results_dict[key]) > 0:
            scores[key] = sum(results_dict[key]) / len(results_dict[key])

    # Get the selected learning rate
    selected_l = max(scores, key=lambda key: scores[key])

    # store the confusion matrix results for the selected k using the CV data
    model_results = {}
    model_results["algorithm"] = "ADABOOST"
    model_results["cv_mean_auc"] = scores[selected_l]
    model_results["parameters"] = {"learning rate": selected_l}
    model_results["confusion_matrix"] = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}

    for train_index, cv_index in kf.split(X_train):
        abc = AdaBoostClassifier(n_estimators=50, learning_rate=selected_l)
        ADAmodel = abc.fit(X_train.iloc[train_index], y_train.iloc[train_index])
        predicted = ADAmodel.predict(X_train.iloc[cv_index])
        true_labels = y_train.iloc[cv_index]

        # True Positive (TP): we predict a label of 1 (positive), and the true label is 1.
        model_results["confusion_matrix"]["tp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 1)
        )

        # True Negative (TN): we predict a label of 0 (negative), and the true label is 0.
        model_results["confusion_matrix"]["tn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 0)
        )

        # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
        model_results["confusion_matrix"]["fp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 0)
        )

        # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
        model_results["confusion_matrix"]["fn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 1)
        )

    # fit the entire training data to the selected model for use with the test data
    abc = AdaBoostClassifier(n_estimators=50, learning_rate=selected_l)
    ADAmodel.fit(X_train, y_train)

    # model_results["model"] = ADAmodel

    return model_results, ADAmodel


## Random Forest
## Note: standarizing not needed
## Note: requires dummy coding
## Note: cannot tolerate missing values (imputation or deletion required)
def RF_training(X_train, y_train, CV_folds, seed):

    # use kfold cross validation
    kf = KFold(n_splits=CV_folds, random_state=seed, shuffle=True)

    # try a range of number of classifiers
    n_range = [10, 100, 1000]

    # Save cross validation results
    results_dict = {}

    # Measure performance for each parameter value across the CV folds
    for n in n_range:
        results_dict[n] = []

    for train_index, cv_index in kf.split(X_train):
        for n in n_range:
            # Create a Gaussian Classifier
            clf = RandomForestClassifier(n_estimators=n)
            # Train the model using the training sets y_pred=clf.predict(X_test)
            clf.fit(X_train.iloc[train_index], y_train.iloc[train_index])
            # Predict the response for test dataset
            predicted = clf.predict_proba(X_train.iloc[cv_index])[:, 1]
            true_labels = y_train.iloc[cv_index]

            # using area under the curve as the metric since this was used in the competition
            try:
                results_dict[n].append(roc_auc_score(true_labels, predicted))
            except:
                pass

    # find the learning rate associated with the highest auc
    scores = {}
    for key in sorted(results_dict):
        if len(results_dict[key]) > 0:
            scores[key] = sum(results_dict[key]) / len(results_dict[key])

    # Get the selected learning rate
    selected_n = max(scores, key=lambda key: scores[key])

    # store the confusion matrix results for the selected k using the CV data
    model_results = {}
    model_results["algorithm"] = "RANDOM FOREST"
    model_results["cv_mean_auc"] = scores[selected_n]
    model_results["parameters"] = {"number of estimators": selected_n}
    model_results["confusion_matrix"] = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}

    for train_index, cv_index in kf.split(X_train):
        # Create a Gaussian Classifier
        clf = RandomForestClassifier(n_estimators=selected_n)
        # Train the model using the training sets y_pred=clf.predict(X_test)
        clf.fit(X_train.iloc[train_index], y_train.iloc[train_index])
        # Predict the response for test dataset
        predicted = clf.predict(X_train.iloc[cv_index])
        true_labels = y_train.iloc[cv_index]

        # True Positive (TP): we predict a label of 1 (positive), and the true label is 1.
        model_results["confusion_matrix"]["tp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 1)
        )

        # True Negative (TN): we predict a label of 0 (negative), and the true label is 0.
        model_results["confusion_matrix"]["tn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 0)
        )

        # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
        model_results["confusion_matrix"]["fp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 0)
        )

        # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
        model_results["confusion_matrix"]["fn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 1)
        )

    # fit the entire training data to the selected model for use with the test data
    clf = RandomForestClassifier(n_estimators=selected_n)
    clf.fit(X_train, y_train)

    # model_results["model"] = clf

    return model_results, clf


## SVM:
## Note: standarizing recommended
## Note: requires dummy coding
## Note: cannot tolerate missing values (imputation or deletion required)
def SVM_training(X_train, y_train, CV_folds, seed):

    # use kfold cross validation
    kf = KFold(n_splits=CV_folds, random_state=seed, shuffle=True)

    # try a few kernels
    kernel = ["linear", "poly", "rbf"]

    # Save cross validation results
    results_dict = {}

    # Measure performance for each parameter value across the CV folds
    for k in kernel:
        results_dict[k] = []

    for train_index, cv_index in kf.split(X_train):
        for k in kernel:
            clf = svm.SVC(kernel=k, gamma=2, probability=True)
            clf.fit(X_train.iloc[train_index], y_train.iloc[train_index])
            # Predict the response for test dataset
            predicted = clf.predict_proba(X_train.iloc[cv_index])[:, 1]
            true_labels = y_train.iloc[cv_index]

            # using area under the curve as the metric since this was used in the competition
            try:
                results_dict[k].append(roc_auc_score(true_labels, predicted))
            except:
                pass

    # find the learning rate associated with the highest auc
    scores = {}
    for key in sorted(results_dict):
        if len(results_dict[key]) > 0:
            scores[key] = sum(results_dict[key]) / len(results_dict[key])

    # Get the selected learning rate
    selected_k = max(scores, key=lambda key: scores[key])

    # store the confusion matrix results for the selected k using the CV data
    model_results = {}
    model_results["algorithm"] = "SVM"
    model_results["cv_mean_auc"] = scores[selected_k]
    model_results["parameters"] = {"kernel": selected_k}
    model_results["confusion_matrix"] = {"tn": 0, "fp": 0, "fn": 0, "tp": 0}

    for train_index, cv_index in kf.split(X_train):
        clf = svm.SVC(kernel=k, gamma=2, probability=True)
        clf.fit(X_train.iloc[train_index], y_train.iloc[train_index])
        # Predict the response for test dataset
        predicted = clf.predict(X_train.iloc[cv_index])
        true_labels = y_train.iloc[cv_index]

        # True Positive (TP): we predict a label of 1 (positive), and the true label is 1.
        model_results["confusion_matrix"]["tp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 1)
        )

        # True Negative (TN): we predict a label of 0 (negative), and the true label is 0.
        model_results["confusion_matrix"]["tn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 0)
        )

        # False Positive (FP): we predict a label of 1 (positive), but the true label is 0.
        model_results["confusion_matrix"]["fp"] += np.sum(
            np.logical_and(predicted == 1, true_labels == 0)
        )

        # False Negative (FN): we predict a label of 0 (negative), but the true label is 1.
        model_results["confusion_matrix"]["fn"] += np.sum(
            np.logical_and(predicted == 0, true_labels == 1)
        )

    # fit the entire training data to the selected model for use with the test data
    clf = svm.SVC(kernel=k, gamma=2, probability=True)
    clf.fit(X_train, y_train)

    # model_results["model"] = clf

    return model_results, clf


def categorical_to_dummy(in_df, outcome):
    enc = LabelEncoder()
    features = in_df.columns.tolist()[1:]  # exclude the index in the features list
    new_df = in_df.iloc[:,0].to_frame()  # index values to build new df    
    new_df[outcome] = in_df[outcome]
    encoding_dict = {}
    for feature in features:
        if feature != outcome:
            if is_numeric_dtype(in_df[feature]):
                new_df[feature] = in_df[feature]
            else:
                # label encode values
                print(in_df[feature])
                new_df[feature] = enc.fit_transform(in_df[feature])
                encoding_dict[feature] = list(enc.classes_)
    return new_df, encoding_dict


def encode_test_data(df, encoding):
    print(len(df))
    for feature, classes_ in encoding.items():
        # find rows that don't match any of the values in the list of classes_
        # remove them
        # return a series indicating if the row has membership in classes_
        non_membership = df[~df[feature].isin(classes_)].index
        # drop the rows
        print(feature)
        print(non_membership)
        df = df.drop(non_membership)

        # encode remaining rows
        enc = LabelEncoder()
        enc.classes_ = classes_
        df[feature] = enc.transform(df[feature])

    print(len(df))
    print(df.head())
    return df

# split the data into training and test
def training_test_split(in_df, outcome, test_prop, seed):
    X = in_df.loc[:, in_df.columns != outcome]
    y = in_df[outcome]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_prop, random_state=seed
    )
    return [X_train, X_test, y_train, y_test]


def split_dataset(df, label, split_percent=0.70):
    y = df[label]
    X = df.drop(label)
    return train_test_split(X, y, test_size=split_percent)


# imputes missing data for testing purposes (since we already have this in our pipeline)
def impute_missing(in_df, numeric_method, categorical_method):
    in_data = in_df.copy()
    features = list(in_data)
    for feature in features:
        if is_numeric_dtype(in_data[feature]):
            if in_data[feature].nunique() > 2:
                imputer = SimpleImputer(missing_values=np.nan, strategy=numeric_method)
                imputer = imputer.fit(in_data[feature].to_frame())
                in_data[feature] = imputer.transform(in_data[feature].to_frame())
            else:
                in_data[feature] = np.array(in_data[feature], dtype=bool)
        else:
            if categorical_method == "mode":
                imputer = SimpleImputer(missing_values=np.nan, strategy="most_frequent")
                imputer = imputer.fit(in_data[feature].to_frame())
                in_data[feature] = imputer.transform(in_data[feature].to_frame())
            elif categorical_method == "missing":
                in_data[feature].fillna("Missing as Category", inplace=True)
    return in_data


# Standardizes all numeric features such that each feature mean = 0 and variance = 1
def standardize_numeric_features(in_df):
    in_data = in_df.copy()
    features = list(in_data)
    scaler = preprocessing.StandardScaler()
    for feature in features:
        if is_numeric_dtype(in_data[feature]) and in_data[feature].nunique() > 2:
            in_data[feature] = scaler.fit_transform(in_data[feature].to_frame())
    return in_data


def data_prep(train_in, ident_in, outcome, impute, standard, dummy):
    # read data
    train_transaction = pd.read_csv(train_in, index_col=0)
    train_id = pd.read_csv(ident_in, index_col=0)
    in_df = train_transaction.merge(
        train_id, how="left", left_on="TransactionID", right_on="TransactionID"
    )

    out_df = in_df.copy()
    # imputation - in future refactoring, put after test split (if possible)
    if impute:
        out_df = impute_missing(in_df, "median", "missing")

    in_df = out_df.copy()
    # standardize - in future refactoring, put after test split (if possible)
    if standard:
        out_df = categorical_to_dummy(in_df, outcome)

    in_df = out_df.copy()
    # dummy code the categorical variables (into binary vars)
    if dummy:
        out_df = categorical_to_dummy(in_df, outcome)

    return out_df


"""    

test_prop = .3
CV_folds = 10
outcome = 'isFraud'
seed = 42


full_df = data_prep('train_transaction.csv', 'train_identity.csv', outcome, True, True, True)
small_df = data_prep('transaction_small.csv', 'identity_small.csv', outcome, True, True, True)


# training & test data split
X_train, X_test, y_train, y_test = training_test_split(small_df, outcome, test_prop)

# Run the ML models
knn_model = KNN_training(X_train, y_train, CV_folds)
ada_model = ADA_training(X_train, y_train, CV_folds)
rf_model = RF_training(X_train, y_train, CV_folds)
svm_model = SVM_training(X_train, y_train, CV_folds)
#xgb_model = XGB_training(X_train, y_train, CV_folds)
"""
