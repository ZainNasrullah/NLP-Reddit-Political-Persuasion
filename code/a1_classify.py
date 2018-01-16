from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.metrics import confusion_matrix
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
    data = np.load(filename)
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
    print('TODO Section 3.2')

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
    print('TODO Section 3.3')

def class34( filename, i ):
    ''' This function performs experiment 3.4

    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)
        '''
    print('TODO Section 3.4')

if __name__ == "__main__":
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    X_train, X_test, y_train, y_test,iBest = class31(args.input)
