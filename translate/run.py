import sys
from os import fdopen

from bf.tokenize import Tokenize
from bf.parse import parse
from bf.run import run


def entry_point(argv):
    """
    entry_point(argv: list[str]) -> int
    """
    filename = argv[1]
    with open(filename) as f, fdopen(0) as stdin, fdopen(1, "w") as stdout:
        program = parse(Tokenize(f))
        run(program, stdin, stdout)
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
