import sys
from helpers import load_pipeline
from engine import QuestionEngine
import codecs
import locale

encoding = locale.getpreferredencoding()
sys.stdin = codecs.getreader(encoding)(sys.stdin)
sys.stdout = codecs.getwriter(encoding)(sys.stdout)

USAGE = "usage: {} [model.pkl] [morphodita_tagger.model]"


def main():
    if len(sys.argv) < 2:
        sys.stdout.write(USAGE.format(sys.argv[0]) + '\n')
        sys.exit(0)

    model_path = sys.argv[2]
    pipeline = load_pipeline(sys.argv[1])
    engine = QuestionEngine(model_path=model_path,
                            pipeline=pipeline)

    not_eof = True
    while not_eof:
        text = ''
        while True:
            line = sys.stdin.readline()
            not_eof = bool(line)
            if not not_eof:
                break
            line = line.rstrip('\n')
            line = line.rstrip('\r')
            text += line
            text += '\n'
            if not line:
                break

        for question in engine.generate_questions(text):
            sys.stdout.write(unicode(question))
            sys.stdout.write('\n')
