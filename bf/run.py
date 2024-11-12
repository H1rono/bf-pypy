import sys
from argparse import ArgumentParser

from . import tokenize
from .machine import Machine
from .parse import parse, ParseResult
from .token import Token


class Position(object):
    def __init__(self, at = 0):
        self.at = at


def run_token(position, machine, token, program):
    """
    run_token(position: Position, machine: Machine, token: Token, program: ParseResult) -> None
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    # assert isinstance(position, Position)
    # assert isinstance(machine, Machine)
    # assert isinstance(token, Token)
    # assert isinstance(program, ParseResult)
    raw = token.raw
    # assert token not in [LOOP_BEGIN, LOOP_END]
    v = machine.tape.value()
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
            position.at = program.bracket_map[position.at]
    elif raw == LOOP_END:
        if v != 0:
            position.at = program.bracket_map[position.at]


def run(program, stdin, stdout):
    """
    run(program: ParseResult, stdin: File, stdout: File) -> None
    """
    assert isinstance(program, ParseResult)
    machine = Machine(stdin, stdout)
    pos = Position()
    while pos.at < len(program.tokens):
        token = program.tokens[pos.at]
        run_token(pos, machine, token, program)
        pos.at += 1


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
