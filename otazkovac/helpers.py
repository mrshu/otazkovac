from sklearn.externals import joblib


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


def load_pipeline(path):
    return joblib.load(path)
