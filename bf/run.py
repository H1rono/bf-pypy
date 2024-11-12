import sys
from argparse import ArgumentParser

from . import tokenize
from .machine import Machine
from .parse import parse, ParseResult
from .token import Token


class Frames(object):
    __slots__ = ["pos", "_machine", "_program"]

    def __init__(self, machine, program):
        assert isinstance(machine, Machine)
        assert isinstance(program, ParseResult)
        self.pos = -1
        self._machine = machine
        self._program = program

    def __iter__(self):
        return self

    def next(self):
        self.pos += 1
        if self.pos >= len(self._program.tokens):
            raise StopIteration()
        return (self.pos, self._machine, self._program)


def run_token(position, machine, token, program):
    """
    run_token(position: int, machine: Machine, token: Token, program: ParseResult) -> int
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    # assert isinstance(position, Position)
    # assert isinstance(machine, Machine)
    # assert isinstance(token, Token)
    # assert isinstance(program, ParseResult)
    raw, _ = token
    # assert token not in [LOOP_BEGIN, LOOP_END]
    v = machine.tape.value()
    npos = position
    if raw == INCREMENT:
        machine.tape.set_value(v + 1)
    elif raw == DECREMENT:
        machine.tape.set_value(v - 1)
    elif raw == ADVANCE:
        machine.tape.advance_by(1)
    elif raw == DEVANCE:
        machine.tape.devance_by(1)
    elif raw == WRITE:
        machine.write()
    elif raw == READ:
        machine.read()
    elif raw == LOOP_BEGIN:
        if v == 0:
            npos = program.bracket_map[position]
    elif raw == LOOP_END:
        if v != 0:
            npos = program.bracket_map[position]
    return npos


def run(program, stdin, stdout):
    """
    run(program: ParseResult, stdin: File, stdout: File) -> None
    """
    assert isinstance(program, ParseResult)
    it = Frames(Machine(stdin, stdout), program)
    for position, machine, program in it:
        token = program.tokens[position].as_tuple()
        p = run_token(position, machine, token, program)
        it.pos = p


def set_args(parser):
    """
    set_args(parser: ArgumentParser) -> None
    """
    assert isinstance(parser, ArgumentParser)
    parser.add_argument()


def main():
    parser = ArgumentParser("parse")
    tokenize.set_args(parser)
    args = parser.parse_args()
    with tokenize.acquire_from_args(args) as t:
        program = parse(t)
        run(program, sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
