"""
run with JIT
"""

import sys
from os import fdopen

from bf.parse import parse
from bf.runjit import run
from bf.tokenize import Tokenize


def entry_point(argv):
    """
    entry_point(argv: list[str]) -> int
    """
    filename = argv[1]
    with open(filename) as f:
        program = parse(Tokenize(f))
    with fdopen(0) as stdin, fdopen(1, "w") as stdout:
        run(program, stdin, stdout)
    return 0


def target(*args):
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


if __name__ == "__main__":
    entry_point(sys.argv)
