"""
```bash
$ cat tmp/test.b
+++
hoge
[+++>>>,,---]
```

```python
>>>> from bf.tokenize import Tokenize
>>>> from bf.parse import Parser
>>>> with open("tmp/test.b", mode="r") as f:
....     t = Tokenize(f)
....     p = Parser()
....     p = list(p.parse(t))
....
>>>> for e in p:
....     print e
....
Program.token(+)
Program.token(+)
Program.token(+)
Program.loop[Program.token(+), Program.token(+), Program.token(+), Program.token(>), Program.token(>), Program.token(>), Program.token(,), Program.token(,), Program.token(-), Program.token(-), Program.token(-)]
```

```bash
$ pypy -m bf.parse < tmp/test.b
Program.token(+)
Program.token(+)
Program.token(+)
Program.loop[Program.token(+), Program.token(+), Program.token(+), Program.token(>), Program.token(>), Program.token(>), Program.token(,), Program.token(,), Program.token(-), Program.token(-), Program.token(-)]
```
"""

from argparse import ArgumentParser

from . import token, tokenize, program
from .tokenize import Tokenize


class Parser(object):
    def __init__(self):
        pass

    def parse(self, tokenize):
        """
        parse(self, tokenize: Tokenize) -> Parsed
        """
        return Parsed(self, tokenize)


class Parsed(object):
    def __init__(self, parser, tokenize, until=None):
        """
        __init__(self, parser: Parser, tokenize: Tokenize, until: Token | None = None)
        """
        assert isinstance(parser, Parser)
        assert isinstance(tokenize, Tokenize)
        assert until is None or token.is_token(until)
        self._parser = parser
        self._tokenize = tokenize
        self._until = until
        # self._inner: Parsed | None
        self._inner = None

    def __iter__(self):
        """
        __iter__(self) -> Self
        # Self: Iterator<Item=Program>
        """
        return self

    def _nest_loop(self):
        """
        nest_loop(self) -> Self
        """
        return Parsed(
            self._parser,
            self._tokenize,
            token.LOOP_END,
        )

    def next(self):
        t = self._tokenize.next()
        assert token.is_token(t)
        if token.is_token(self._until) and t == self._until:
            raise StopIteration()
        if t == token.LOOP_BEGIN:
            loop = program.loop(self._nest_loop())
            return loop
        assert t not in [token.LOOP_BEGIN, token.LOOP_END]
        return program.token(t)

    def collect(self):
        """
        collect(self) -> list[Program]
        """
        return [p for p in self]


def set_parse_args(parser):
    """
    set_parse_args(parser: ArgumentParser) -> None
    """
    tokenize.set_args(parser)


def main():
    parser = ArgumentParser("parse")
    tokenize.set_args(parser)
    args = parser.parse_args()
    parser = Parser()
    with tokenize.acquire_from_args(args) as t:
        program = parser.parse(t).collect()
    for e in program:
        print e


if __name__ == "__main__":
    main()
