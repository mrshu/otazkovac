# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsOneClassifier
from sklearn import cross_validation
import sklearn.metrics
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier

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


def tokenize(input):
    lemmas = input.split()
    tokens = [lemma.split('/')[0] for lemma in lemmas]
    tokens = list(part for token in tokens for part in token)
    return tokens

np.random.seed(42)

vectorizers = [
    (CountVectorizer(ngram_range=(2, 3),
                     tokenizer=tokenize), '2-3 normal'),
    (CountVectorizer(ngram_range=(2, 4),
                     tokenizer=tokenize), '2-4 normal'),
    (CountVectorizer(analyzer=otazkovac.helpers.special_unigrams_bigrams),
     '1-4 specia'),
    (CountVectorizer(ngram_range=(2, 4),
                     tokenizer=otazkovac.helpers.tokenize),
     '2-4 revers'),
    (CountVectorizer(ngram_range=(2, 3),
                     tokenizer=otazkovac.helpers.tokenize),
     '2-3 revers'),
]

classifiers = [
    MultinomialNB(),
    RandomForestClassifier(),
    LinearSVC(loss='squared_hinge', penalty='l2', dual=False, tol=1e-4),
]

pipelines = []

for (v, name) in vectorizers:
    # print "> Running tests with {}".format(v)
    print
    print name,
    for classifier in classifiers:
        # print "  > Using classifier {}".format(classifier)
        pipeline = Pipeline([('vect', v),
                            ('clf', OneVsOneClassifier(classifier))])

        accuracies = cross_validation.cross_val_score(pipeline, csv[1], csv[2],
                                                      cv=10)
        print '    {:.2f}'.format(accuracies.mean()*100,
                                  accuracies.std()*200),

        pipeline = Pipeline([('vect', v),
                             ('clf', OneVsOneClassifier(classifier))])
        pipelines.append(pipeline)

print
print "Full dataset:"
pipelines[-1].fit(np.asarray(csv[1]), np.asarray(csv[2]))
print "Full dataset accuracy: {}".format(pipelines[-1].score(csv[1], csv[2]))

predicted = pipelines[-1].predict(csv[1])

print "Classification report:"
print sklearn.metrics.classification_report(csv[2], predicted)

print "Confusion matrix:"
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
