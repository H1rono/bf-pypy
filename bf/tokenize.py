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
        self._program = iter(program)

    def __iter__(self):
        """
        __iter__(self) -> Generator<Item=Token>
        """
        for line in self._program:
            assert isinstance(line, str)
            tokens = (Token.from_char(c) for c in line)
            tokens = filter(None, tokens)
            for t in tokens:
                yield t

    @staticmethod
    def set_args(parser):
        """
        set_args(parser: ArgumentParser) -> None
        """
        assert isinstance(parser, ArgumentParser)
        parser.add_argument("--program", nargs="?", help="bf program to tokenize; stdin by default")

    @classmethod
    @contextmanager
    def acquire_from_args(cls, args):
        """
        acquire_from_args(cls, args) -> Tokenize
        """
        assert hasattr(args, "program")
        program = args.program
        assert program is None or isinstance(program, str)
        try:
            program = open(program, mode="r") if program is not None else sys.stdin
            yield cls(program)
        finally:
            program.close()


def main():
    parser = ArgumentParser("tokenize")
    Tokenize.set_args(parser)
    args = parser.parse_args()
    with Tokenize.acquire_from_args(args) as tokenize:
        result = list(iter(tokenize))
    print result


if __name__ == "__main__":
    main()
