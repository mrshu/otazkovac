import sys
from helpers import load_pipeline
from engine import QuestionEngine
import codecs
import locale
import click

encoding = locale.getpreferredencoding()
sys.stdin = codecs.getreader(encoding)(sys.stdin)
sys.stdout = codecs.getwriter(encoding)(sys.stdout)


def serve(engine):
    from flask import Flask, request, jsonify
    app = Flask('otazkovac')

    @app.route('/questions', methods=['POST'])
    def generate_questions():
        if 'text' not in request.values:
            return jsonify({'error': 'Missing text parameter'})
        text = request.values['text']
        questions = []
        for q in engine.generate_questions(text):
            questions.append(q.to_dict())

        return jsonify({'questions': {
            'count': len(questions),
            'entries': questions
        }})

    app.run()


def text_from_stdin(engine):
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


@click.command()
@click.option('--morpho-model', required=True,
              help='Path to the MorphoDita Slovak tagger model')
@click.option('--pipeline', required=True,
              help='Path to the saved pipeline')
@click.option('--server', is_flag=True,
              help='Start otazkovac as a server')
@click.option('--debug', is_flag=True,
              help='Turn on debugging output')
def main(morpho_model, pipeline, server, debug):

    model_path = morpho_model
    pipeline = load_pipeline(pipeline)
    engine = QuestionEngine(model_path=model_path,
                            pipeline=pipeline,
                            debug=debug)

    if server:
        serve(engine)
    else:
        text_from_stdin(engine)
