# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import (TfidfVectorizer, CountVectorizer,
                                             HashingVectorizer)

from sklearn.cross_validation import ShuffleSplit
from sklearn.svm import LinearSVC, SVC
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsOneClassifier
from sklearn import cross_validation
import sklearn.metrics
from sklearn import preprocessing
from sklearn.externals import joblib

from mlxtend.classifier import EnsembleClassifier

import sys
import pandas as pd
import numpy as np
import re
import os

import otazkovac

if len(sys.argv) < 2:
    print "usage: {} [FILE.csv]".format(sys.argv[0])
    sys.exit(0)

f = sys.argv[1]
csv = pd.read_csv(f, header=None, encoding='utf-8', sep='\t')


vectorizers = [

    CountVectorizer(ngram_range=(2, 3),
                    tokenizer=otazkovac.helpers.tokenize),
    CountVectorizer(ngram_range=(2, 4),
                    tokenizer=otazkovac.helpers.tokenize),
    CountVectorizer(analyzer=otazkovac.helpers.special_unigrams_bigrams)
]

classifiers = [
    MultinomialNB(),
    SGDClassifier(loss='squared_hinge', penalty='l2', alpha=1e-4, n_iter=10),
    LinearSVC(loss='squared_hinge', penalty='l2', dual=False, tol=1e-4),
]

pipelines = []


splitter = ShuffleSplit(csv.shape[0], n_iter=10, test_size=0.2)
for v in vectorizers:
    print "> Running tests with {}".format(v)
    for classifier in classifiers:
        print "  > Using classifier {}".format(classifier)
        accuracies = []
        f1s = []

        for train, test in splitter:
            pipeline = Pipeline([('vect', v),
                                 ('tfidf', TfidfTransformer(sublinear_tf=True,
                                                            use_idf=False)),
                                 ('clf', OneVsOneClassifier(classifier))])

            pipeline.fit(np.asarray(csv[1][train]),
                         np.asarray(csv[2][train]))

            y_test = csv[2][test]
            X_test = csv[1][test]

            accuracies.append(pipeline.score(X_test, y_test))

        accuracies = np.array(accuracies)
        f1s = np.array(f1s)
        print '    > Accuracy: {} ({})'.format(accuracies.mean(),
                                               accuracies.std()*2)
        pipeline = Pipeline([('vect', v),
                             ('tfidf', TfidfTransformer(sublinear_tf=True,
                                                        use_idf=False)),
                             ('clf', classifier)])
        pipelines.append(pipeline)

accuracies = []
for train, test in splitter:
    pipeline = EnsembleClassifier(clfs=pipelines, voting='hard')

    pipeline.fit(np.asarray(csv[1][train]),
                 np.asarray(csv[2][train]))

    y_test = csv[2][test]
    X_test = csv[1][test]

    accuracies.append(pipeline.score(X_test, y_test))
accuracies = np.array(accuracies)
print '    > Accuracy: {} ({})'.format(accuracies.mean(),
                                       accuracies.std()*2)

print "Full dataset:"
pipelines[-1].fit(np.asarray(csv[1]), np.asarray(csv[2]))
print "Full dataset accuracy: {}".format(pipelines[-1].score(csv[1], csv[2]))

predicted = pipelines[-1].predict(csv[1])
print sklearn.metrics.confusion_matrix(csv[2], predicted)

print "Incorrect classifications:"
for row in csv.iterrows():
    sentence = row[1][0]
    lem = row[1][1]
    true = row[1][2]
    pred = pipelines[-1].predict([lem])[0]
    if pred != true:
        print unicode(sentence), unicode(lem), pred, true
joblib.dump(pipelines[-1], 'pipeline.pkl', compress=9)
