# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import (TfidfVectorizer, CountVectorizer,
                                             HashingVectorizer)

from sklearn.cross_validation import ShuffleSplit
from sklearn.svm import LinearSVC, SVC
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

if len(sys.argv) < 2:
    print "usage: {} [FILE.csv]".format(sys.argv[0])
    sys.exit(0)

f = sys.argv[1]
csv = pd.read_csv(f, header=None, encoding='utf-8', sep='\t')


def tokenize(input):
    lemmas = input.split()
    tokens = [list(reversed(lemma.split('/'))) for lemma in lemmas]
    tokens = list(part for token in tokens for part in token)
    return tokens


def special_unigrams_bigrams(text):
    tokens = tokenize(text)

    for n in range(1, 4):
        for i in range(0, len(tokens)-n):
            yield ' '.join(tokens[i:i+n+1])

    if len(tokens) > 4:
        yield ' '.join(tokens[:2] + tokens[len(tokens) - 2:])
        yield ' '.join(tokens[:2] + tokens[len(tokens) - 1:])
        yield ' '.join(tokens[:1] + tokens[len(tokens) - 2:])
        yield ' '.join(tokens[:1] + tokens[len(tokens) - 1:])


vectorizers = [

    CountVectorizer(ngram_range=(2, 3),
                    tokenizer=tokenize),
    CountVectorizer(ngram_range=(2, 4),
                    tokenizer=tokenize),
    CountVectorizer(analyzer=special_unigrams_bigrams)
]

classifiers = [
    LinearSVC(loss='l2', penalty='l2', dual=False, tol=1e-4),
]

pipelines = []


splitter = ShuffleSplit(csv.shape[0], n_iter=10, test_size=0.2)
for v in vectorizers:
    print "> Running tests with {}".format(v)
    for classifier in classifiers:
        # print "  > Using classifier {}".format(classifier)
        accuracies = []
        f1s = []

        for train, test in splitter:
            pipeline = Pipeline([('vect', v),
                                 ('tfidf', TfidfTransformer(sublinear_tf=True,
                                                            use_idf=False)),
                                 ('clf', classifier)])

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
print "Full accuracy: {}".format(pipelines[-1].score(csv[1], csv[2]))

joblib.dump(pipelines[-1], 'pipeline.pkl', compress=9)
