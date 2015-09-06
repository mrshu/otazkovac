import sys
import codecs
import locale

from ufal.morphodita import *


def encode_entities(text):
    return text.replace('&', '&amp;').replace('<', '&lt;') \
            .replace('>', '&gt;').replace('"', '&quot;')

encoding = locale.getpreferredencoding()
sys.stdin = codecs.getreader(encoding)(sys.stdin)
sys.stdout = codecs.getwriter(encoding)(sys.stdout)

if len(sys.argv) == 1:
    sys.stderr.write('Usage: %s tagger_file\n' % sys.argv[0])
    sys.exit(1)

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


text = file(sys.argv[2]).read().decode('utf-8')

# Tag
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
        # sys.stdout.write('%s - %s\n' % (lemma.tag, selected_text))

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
        sys.stdout.write("\n")
        sys.stdout.write(sentence + '\t' + lem)
sys.stdout.write(encode_entities(text[t:]))
