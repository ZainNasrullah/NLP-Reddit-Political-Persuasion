import numpy as np
import sys
import argparse
import os
import json

import re
import csv

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.feature_extraction.text import CountVectorizer


from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression

# Load the models
svcLinear = LinearSVC()
svcRBF = SVC(kernel='rbf')
rf = RandomForestClassifier(n_estimators=10, max_depth=5)
mlp = MLPClassifier(alpha=0.05)
adaboost = AdaBoostClassifier()
lr = LogisticRegression()

models = [svcLinear, rf, adaboost, lr]

# Open the stop words path
stopWordPath = '/u/cs401/Wordlists/abbrev.english'
Windows = True
if Windows:
    stopWordPath = 'G:\\OneDrive - University of Toronto\\MScAC\\NLP\\NLP-Reddit-Political-Persuasion\Wordlists\\StopWords'

with open(stopWordPath, "r") as file:
    stop = file.read().split('\n')


def main(args):

    # load the data
    data = json.load(open(args.input))
    category = {'Left': 0, 'Center': 1, 'Right': 2, 'Alt': 3}

    comments = []
    labels = []

    # TODO: Iterate through comments in JSON file
    for i, comment in enumerate(data):
        comments.append(comment['body'])
        labels.append(category[comment['cat']])

    # Create numpy arrays containing comments and labels
    X = np.array(comments)
    Y = np.array(labels)

    with open('a1_bonus.csv', 'w', newline='') as file:
        writer = csv.writer(file)

    ngram_list = [(1, 1), (2, 2)]

    for ngram in ngram_list:
        # Transform the comments array into the bag of words model
        count = CountVectorizer(ngram_range=ngram, stop_words=stop)
        X_bag = count.fit_transform(X)

        # Calculate the cross-validation scores for each model
        # format: (model, mean score, scores across folds)
        scores = []
        for i, model in enumerate(models):
            cv = KFold(5, shuffle=True)
            score = cross_val_score(model, X_bag, Y, cv=cv)
            score_summary = [i + 1, score.mean()]
            score_summary.extend(score)
            print(score_summary)
            scores.append(score_summary)

        with open('a1_bonus.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(scores)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument(
        "-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()

    main(args)
