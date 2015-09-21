import sys

USAGE = "usage: {} [model.pkl] [morphodita_tagger.model]"


def main():
    if len(sys.argv) < 2:
        sys.stdout.write(USAGE.format(sys.argv[0]))
        sys.exit(0)

    tagger = Tagger.load(sys.argv[1])
    if not tagger:
        sys.stderr.write("Cannot load tagger from file '%s'\n" % sys.argv[1])
        sys.exit(1)
        sys.stderr.write('done\n')

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
                    taking = False
                    capturing = False
                    sentence = ''

                if len(lemma.tag) > 4 and last_num != lemma.tag[4]:
                    capturing = False

                if lemma.tag[0] == 'E' and lemma.tag[4] == '6' and i == 0:
                    taking = True
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
            if sentence != '' and sentence.endswith('.'):
                sys.stdout.write(sentence)
