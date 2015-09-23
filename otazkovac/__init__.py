import sys
from ufal.morphodita import *
from helpers import load_pipeline
import codecs
import locale
import re

encoding = locale.getpreferredencoding()
sys.stdin = codecs.getreader(encoding)(sys.stdin)
sys.stdout = codecs.getwriter(encoding)(sys.stdout)

USAGE = "usage: {} [model.pkl] [morphodita_tagger.model]"


def main():
    if len(sys.argv) < 2:
        sys.stdout.write(USAGE.format(sys.argv[0]))
        sys.exit(0)

    tagger = Tagger.load(sys.argv[2])
    if not tagger:
        sys.stderr.write("Cannot load tagger from file '%s'\n" % sys.argv[2])
        sys.exit(1)
        sys.stderr.write('done\n')

    pipeline = load_pipeline(sys.argv[1])

    mapping = {
        u'T': 'Kedy',
        u'P': 'Kde'
    }

    forms = Forms()
    lemmas = TaggedLemmas()
    tokens = TokenRanges()
    tokenizer = tagger.newTokenizer()
    if tokenizer is None:
        sys.stderr.write("No tokenizer is defined for the supplied model!")
        sys.exit(1)

    not_eof = True
    while not_eof:
        text = ''
        while True:
            line = sys.stdin.readline()
            not_eof = bool(line)
            if not not_eof:
                break
            line = line.rstrip('\r\n')
            text += line
            text += '\n'
            if not line:
                break

        tokenizer.setText(text)
        t = 0
        while tokenizer.nextSentence(forms, tokens):
            tagger.tag(forms, lemmas)

            sentence = ''
            lem = ''
            last_num = ''
            taking = False
            capturing = False

            for i in range(len(lemmas)):
                lemma = lemmas[i]
                token = tokens[i]
                selected_text = text[token.start: token.start + token.length]

                if selected_text == ',':
                    taking = True
                    capturing = False
                    sentence = ''

                if len(lemma.tag) > 4 and last_num != lemma.tag[4]:
                    taking = True
                    capturing = False

                if lemma.tag[0] == 'E' and lemma.tag[4] == '6' and i == 0:
                    taking = False
                    capturing = True
                    last_num = '6'

                if taking:
                    sentence += selected_text + ' '

                if capturing:
                    lem += lemma.lemma + '/' + lemma.tag + ' '

                if len(lemma.tag) > 4:
                    last_num = lemma.tag[4]

                t = token.start + token.length
            sentence = sentence.strip()

            if sentence != '' and sentence.endswith('.') and lem != '':
                predicted = pipeline.predict([lem])[0]
                if predicted == u'I':
                    continue

                sentence = re.sub('^\s*\,\s*', '', sentence)
                sentence = mapping[predicted] + ' ' + sentence
                sentence = re.sub('\s*\.$', '?', sentence)

                sys.stdout.write(sentence + '\n')
