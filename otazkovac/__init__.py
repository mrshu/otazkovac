import sys

USAGE = "usage: {} [model.pkl] [morphodita_tagger.model]"


def main():
    if len(sys.argv) < 2:
        print USAGE.format(sys.argv[0])
        sys.exit(0)
