import os
import sys

from bf.parse import parse
from bf.run import run
from bf.token import Tokens


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp:
        program, metadata = parse(Tokens(fp))
    with os.fdopen(0, 'r') as stdin, os.fdopen(1, 'w') as stdout:
        run(program, metadata, stdin, stdout)
    return 0


def target(*args):
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


if __name__ == "__main__":
    entry_point(sys.argv)
