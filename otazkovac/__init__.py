import sys


def main():
    if len(sys.argv) < 2:
        print "usage: {} [model.pkl] [morphodita.model]".format(sys.argv[0])
        sys.exit(0)
