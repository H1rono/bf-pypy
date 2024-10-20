"""
```bash
pypy -m bf.tokenize --program test.b
```
"""


from argparse import ArgumentParser
from contextlib import contextmanager
import sys

from . import token
from .token import Token


class Tokenize(object):
    def __init__(self, program):
        """
        __init__(self, program: Iterator<Item=str>) -> None
        """
        self._program = program
        # self._current_line: str | None
        self._current_line = ''

    def __iter__(self):
        """
        __iter__(self) -> Self
        # Self: Generator<Item=Token>
        """
        return self

    def next(self):
        """
        next(self) -> Token
        throws StopIteration
        """
        # t: Token | None
        t = None
        while t is None and not token.is_token(t):
            if self._current_line is None or len(self._current_line) == 0:
                self._current_line = self._program.readline(100)
            if len(self._current_line) == 0:
                raise StopIteration()
            head = self._current_line[0]
            rest = self._current_line[1:]
            t = token.from_char(head)
            self._current_line = rest
        return t


def set_args(parser):
    """
    set_args(parser: ArgumentParser) -> None
    """
    assert isinstance(parser, ArgumentParser)
    parser.add_argument("--program", nargs="?", help="bf program to tokenize; stdin by default")


@contextmanager
def acquire_from_args(args):
    """
    @contextmanager
    acquire_from_args(args) -> Tokenize
    """
    assert hasattr(args, "program")
    program = args.program
    assert program is None or isinstance(program, str)
    try:
        program = open(program, mode="r") if program is not None else sys.stdin
        yield Tokenize(program)
    finally:
        program.close()


def main():
    parser = ArgumentParser("tokenize")
    tokenize.set_args(parser)
    args = parser.parse_args()
    with tokenize.acquire_from_args(args) as tokenize:
        result = list(iter(tokenize))
    print result


if __name__ == "__main__":
    main()
