from argparse import ArgumentParser

from . import tokenize
from .token import Token, LOOP_BEGIN, LOOP_END
from .tokenize import Tokenize


class ParseResult(object):
    __slots__ = ["tokens", "bracket_map", "raw"]

    def __init__(self, tokens, bracket_map):
        self.tokens = tokens
        self.bracket_map = bracket_map
        self.raw = "".join([t.raw for t in self.tokens])


def parse(tokenize):
    assert isinstance(tokenize, Tokenize)
    tokens = []
    bracket_map = {}
    loop_nests = []
    it = tokenize.enumerate()
    for i, token in it:
        tokens.append(token)
        if token.raw == LOOP_BEGIN:
            loop_nests.append(i)
        elif token.raw == LOOP_END:
            begin_i = loop_nests.pop(-1)
            bracket_map[i] = begin_i
            bracket_map[begin_i] = i
    return ParseResult(tokens, bracket_map)


def main():
    parser = ArgumentParser("parse")
    tokenize.set_args(parser)
    args = parser.parse_args()
    with tokenize.acquire_from_args(args) as t:
        result = parse(t)
    print result.bracket_map
    for e in result.tokens:
        print e.as_tuple()


if __name__ == "__main__":
    main()
