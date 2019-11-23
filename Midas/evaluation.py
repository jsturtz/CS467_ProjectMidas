#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input:  
    x_test: observations for evaluating a particular model
    y_test: the true labels (outcome)
    model: the model to use to make predictions
    roc_filename: the output filename of the ROC image
    
Returns:
    a dictionary including a classification report,
    confusion matrix, counts of false positives, false negatives,
    true positives, true negatives, accuracy
    
    Also saves an image ROC curve

References:
    
#https://stackoverflow.com/questions/25009284/how-to-plot-roc-curve-in-python
#https://scikit-learn.org/stable/modules/model_evaluation.html
https://en.wikipedia.org/wiki/Receiver_operating_characteristic
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html

"""

import numpy as np
from sklearn.metrics import roc_curve
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import matplotlib as mpl
mpl.use('Agg')

def evaluation(x_test, y_test, model, roc_filename):
    # get 0/1 predictions
    y_pred = model["model"].predict(x_test)
    # get probability predictions
    y_pred_proba = model["model"].predict_proba(x_test)[::,1]
    
    results = {}
    results["Classification Report"]  = classification_report(y_test, y_pred)
    results["Confusion Matrix"] = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    results["True Negatives"] = tn
    results["False Positives"] = fp
    results["False Negatives"] = fn
    results["True Positives"] = tp
    fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)
    auc = metrics.roc_auc_score(y_test, y_pred_proba)
    results["Accuracy"] = metrics.accuracy_score(y_test, y_pred)
    
    try:
        plt.title('Receiver Operating Characteristic')
        plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % auc)
        plt.legend(loc = 'lower right')
        plt.plot([0, 1], [0, 1],'r--')
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.savefig(roc_filename) 
    except:
        pass
    plt.close('all') 
    return results


#eval_results = evaluation(X_train, y_train, rf_model, "ROC.png")