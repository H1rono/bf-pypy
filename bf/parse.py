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
from .program import Program
from .tokenize import Tokenize


class Parser(object):
    def __init__(self):
        pass

    def _parse_loop(self, it):
        """
        _parse_loop(self, it: Iterator<Item=Token>) -> Generator<Item=Program>
        """
        for t in it:
            if t not in [token.LOOP_BEGIN, token.LOOP_END]:
                yield program.token(t)
                continue
            if t == token.LOOP_END:
                return
            # t == token.LOOP_BEGIN
            yield program.loop(self._parse_loop(it))

    def parse(self, tokenize):
        """
        parse(self, tokenize: Tokenize) -> Generator<Item=Program>
        """
        assert isinstance(tokenize, Tokenize)
        it = tokenize
        for t in it:
            if t not in [token.LOOP_BEGIN, token.LOOP_END]:
                yield program.token(t)
                continue
            if t == token.LOOP_END:
                raise ValueError("unexpected end-of-loop")
            assert t == token.LOOP_BEGIN
            yield program.loop(self._parse_loop(it))


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
        program = list(parser.parse(t))
    for e in program:
        print e


if __name__ == "__main__":
    main()
