from ufal.morphodita import *
import re
import codecs
import locale


class QuestionEngine(object):

    """Docstring for QuestionEngine. """

    def __init__(self, model_path, pipeline, mapping=None):
        """"""

        self.pipeline = pipeline

        self.tagger = Tagger.load(model_path)
        if not self.tagger:
            msg = "Cannot load tagger from file '{}'\n".format(model_path)
            raise Exception(msg)

        self.tokenizer = self.tagger.newTokenizer()

        self.mapping = mapping
        if self.mapping is None:
            self.mapping = {
                u'T': 'Kedy',
                u'P': 'Kde'
            }

        if self.tokenizer is None:
            raise Exception("No tokenizer is defined for the supplied model!")

    def generate_questions(self, text):
        self.tokenizer.setText(text)
        t = 0
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()

        while self.tokenizer.nextSentence(forms, tokens):
            self.tagger.tag(forms, lemmas)

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
                predicted = self.pipeline.predict([lem])[0]
                if predicted == u'I':
                    continue

                sentence = re.sub('^\s*\,\s*', '', sentence)
                sentence = self.mapping[predicted] + ' ' + sentence
                sentence = re.sub('\s*\.$', '?', sentence)

                yield sentence
