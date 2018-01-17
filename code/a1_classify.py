from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from scipy import stats

import numpy as np
import argparse
import sys
import os
import csv

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier

# create models with specified hyperparameters
svcLinear = SVC(kernel='linear')
svcRBF = SVC(kernel='rbf')
rf = RandomForestClassifier(n_estimators=10, max_depth=5)
mlp = MLPClassifier(alpha=0.05)
adaboost = AdaBoostClassifier()

# create list to easily call them by index
models = [svcLinear, svcRBF, rf, mlp, adaboost]


def accuracy( C ):
    ''' Compute accuracy given Numpy array confusion matrix C. Returns a floating point value '''

    # return the sum of the diagonal entries divided by the sum of the flattened entire flattened 2D array
    return sum(np.diag(C)) / np.sum(C)

def recall( C ):
    ''' Compute recall given Numpy array confusion matrix C. Returns a list of floating point values '''

    # TP / (TP+FN)
    # numerator is the diagonal entry i,i
    # sum across the cols to get denominator for each class
    return np.diag(C) / C.sum(axis=1)

def precision( C ):
    ''' Compute precision given Numpy array confusion matrix C. Returns a list of floating point values '''

    # TP / (TP+FP)
    # numerator is the diagonal entry i,i
    # sum across the rows to get denminator for each class
    return np.diag(C) / C.sum(axis=0)


def class31(filename):
    ''' This function performs experiment 3.1

    Parameters
       filename : string, the name of the npz file from Task 2

    Returns:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier
    '''
    # load data; separate into features and target
    data = np.load(filename)['arr_0']
    X = data[:,0:173]
    y = data[:, 173]

    # split into 80/20 train-test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    scoreList = []
    accBest = 0
    iBest = None
    # iterate through models
    for i, model in enumerate(models):

        # fit data and then find the confusion matrix
        model.fit(X_train, y_train)
        y_predict = model.predict(X_test)
        cm = confusion_matrix(y_test, y_predict)

        # Apend the model number
        scores = []
        scores.append(i+1)

        # Append accuracy and keep track of best
        acc = accuracy(cm)
        scores.append(acc)
        if acc > accBest:
        accBest = acc
        iBest = i + 1

        # extend the list with class scores for recall, precision
        scores.extend(recall(cm))
        scores.extend(precision(cm))

        # extend the list with a flattened confusion matrix
        scores.extend(cm.flatten())

        # add to list of all models
        scoreList.append(scores)

    # write list of scores for each model to csv
    with open('a1_3.1.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(scoreList)

    return (X_train, X_test, y_train, y_test,iBest)


def class32(X_train, X_test, y_train, y_test,iBest):
    ''' This function performs experiment 3.2

    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)

    Returns:
       X_1k: numPy array, just 1K rows of X_train
       y_1k: numPy array, just 1K rows of y_train
   '''

   # load best model from Q1 and create empty list to store accuracies
    model = models[iBest - 1]
    accuracyList = []

   # iterate through each sample length
    lengths = [1000, 5000, 10000, 15000, 20000]
    for l in lengths:

        # generate a random list of indices of size l in range (0, train size)
        idx = np.random.choice(a=X_train.shape[0], size = l)

        # create random samples using those indices
        X_sample = X_train[idx]
        y_sample = X_test[idx]

        # fit model on the sample, predict on the test set and store accuracy
        model.fit(X_sample, y_sample)
        y_predict = model.predict(X_test)
        cm = confusion_matrix(y_test, y_predict)
        accuracyList.append(accuracy(cm))

    # write accuracies to csv file
    with open('a1_3.2.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows([accuracyList])

    return (X_1k, y_1k)

def class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k):
    ''' This function performs experiment 3.3

    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)
       X_1k: numPy array, just 1K rows of X_train (from task 3.2)
       y_1k: numPy array, just 1K rows of y_train (from task 3.2)
    '''
    model = models[i-1]
    stored_values = []

    for k in [5, 10, 20, 30, 40, 50]:
        # keep track of which k we're on
        pp = [k]

        # create selector object
        selector= SelectKBest(chi2, k)

        # fit selector on 1K training data and print indices of top k features
        selector.fit(X_1K, y_1k)
        idx = selector.pvalues_.argsort()[-k:][::-1]
        print("size= 1K, k=", k, ":", idx)

        # when k is 5, fit using best model and evaluate
        if k == 5:
            # transform train data and fit model
            Xk_1K = selector.transform(X_1K, y_1k)
            model.fit(Xk_1K, y_1k)

            # transform test data and predict
            y_predict = model.predict(selector.transform(X_test))
            cm = confusion_matrix(y_test, y_predict)
            acc_1K = accuracy(cm)

        # fit selector on 32K training data and print indices of top k features
        selector.fit(X_train, y_train)
        idx = selector.pvalues_.argsort()[-k:][::-1]
        print("size= 32K, k=", k, ":", idx)
        print()

        # store top k p-values for the 32k database
        pp.extend(selector.pvalues_[idx])
        stored_values.append(pp)

        # when k is 5, fit using best model and evaluate
        if k == 5:
            # transform train data and fit model
            Xk_32K = selector.transform(X_train, y_train)
            model.fit(Xk_32K, y_train)

            # transform test data and predict
            y_predict = model.predict(selector.transform(X_test))
            cm = confusion_matrix(y_test, y_predict)
            acc_32K = accuracy(cm)

    # finalize the list for writing to csv
    stored_values.append([acc1K, acc32K])

    # write to csv
    with open('a1_3.3.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(stored_values)


def class34( filename, i ):
    ''' This function performs experiment 3.4

    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)
        '''
    # load data; separate into features and target
    data = np.load(filename)['arr_0']
    X = data[:,0:173]
    y = data[:, 173]

    # create KFold object with shuffle and 5 splits
    kf = KFold(n_splits=5, shuffle=True)

    # Iterate across each model
    acc_across_models =[]
    for model in models:

        # list to hold accuracy across folds
        acc_across_folds=[]

        # iterate across folds
        for train_idx, test_idx in kf.split(X):

            # create train and test data for this fold
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # fit model on training data and test on test data
            model.fit(X_train, X_test)
            y_predict = model.predict(X_test)
            cm = confusion_matrix(y_test, y_predict)

            # store accuracy for this fold
            acc_across_folds.append(accuracy(cm))

        # store accuracies for model across folds
        acc_across_models.append(acc_across_folds)

    # identify best classifier and its scores
    best_model_scores = acc_across_models[i-1]

    # create list to hold p values
    p_values=[]

    # iterate through saved scores
    for scores in acc_across_models:

        # save p-values comparing other scores to the best model scores
        if scores is not best_model_scores:
            p_values.append(stats.ttest_rel(best_model_scores,scores)[1])

    # write out all results to a csv file
    acc_across_models.append(p_values)
    with open('a1_3.3.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(acc_across_models)






if __name__ == "__main__":
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    X_train, X_test, y_train, y_test,iBest = class31(args.input)
    X_1k, y_1k = class32(X_train, X_test, y_train, y_test,iBest)
    class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k)

