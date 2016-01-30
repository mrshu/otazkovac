from ufal.morphodita import *
import re


class Question(object):

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u"<Question('{}', answer='{}')>".format(self.question,
                                                       self.answer)


class QuestionEngine(object):
    """A class that holds the actual question generation model."""

    def __init__(self, model_path, pipeline, mapping=None):
        """Initalize the class with given model (loaded from model_path) and
        classification pipeline (from pipeline)."""

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
                u'P': 'Kde',
                u'I': None
            }

        if self.tokenizer is None:
            raise Exception("No tokenizer is defined for the supplied model!")

    def generate_questions(self, text):
        """A function that gets text and returns questions from this text in
        return."""

        self.tokenizer.setText(text)
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()

        while self.tokenizer.nextSentence(forms, tokens):
            self.tagger.tag(forms, lemmas)

            response = ''
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
                    response += selected_text + ' '

                if len(lemma.tag) > 4:
                    last_num = lemma.tag[4]

            sentence = sentence.strip()

            if sentence != '' and sentence.endswith('.') and lem != '':
                predicted = self.pipeline.predict([lem])[0]
                if self.mapping[predicted] is None:
                    continue

                sentence = re.sub('^\s*\,\s*', '', sentence)
                sentence = self.mapping[predicted] + ' ' + sentence
                sentence = re.sub('\s*\.$', '?', sentence)

                # and to be sure ...
                sentence = re.sub('\s*\,', ',', sentence)
                response = response.rstrip()

                yield Question(question=sentence, answer=response)
