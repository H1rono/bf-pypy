import sys
from argparse import ArgumentParser

from . import tokenize, program as bf_program
from .machine import Machine
from .parse import Parser, Parsed
from .program import Program
from .token import is_token


class Context(object):
    __slots__ = ["_machine", "_program", "_current_index", "_current_loop", "_is_loop"]

    def __init__(self, machine, program, is_loop=False):
        """
        __init__(self, machine: Machine, program: list[Program], is_loop: bool)
        """
        assert isinstance(machine, Machine)
        assert isinstance(program, list)
        self._machine = machine
        self._program = program
        self._current_index = 0
        # self._current_loop: Context(is_loop=True) | None
        self._current_loop = None
        self._is_loop = is_loop

    def __iter__(self):
        """
        __iter__(self) -> Self
        # Self: Iterator<Item=Machine>
        """
        return self

    def _inc_index(self):
        """
        _inc_index(self) -> None
        """
        self._current_index += 1
        i = self._current_index
        if self._is_loop:
            self._current_index %= len(self._program)
        return i

    def next(self):
        if self._current_loop is not None:
            # assert isinstance(self._current_loop, Context)
            try:
                n = self._current_loop.next()
            except StopIteration:
                self._current_loop = None
                i = self._inc_index()
                return (self._machine, self._program, i, bf_program.token("]"))
            else:
                return n
        if self._is_loop and self._current_index == 0 and self._machine.tape.value() == 0:
            raise StopIteration()
        try:
            program = self._program[self._current_index]
        except IndexError:
            raise StopIteration()
        if program.kind == Program.KIND_TOKEN:
            # run_token(self._machine, program)
            i = self._inc_index()
            return (self._machine, self._program, i, program)
        assert program.kind == Program.KIND_LOOP
        self._current_loop = Context(self._machine, program.loop, True)
        i = self._current_index + 1
        return (self._machine, self._program, i, bf_program.token("["))


def run_token(machine, token):
    """
    run_token(machine: Machine, token: Program.token) -> None
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    assert isinstance(machine, Machine)
    assert isinstance(token, Program) and token.kind == Program.KIND_TOKEN
    token_inner = token.token
    assert token_inner is not None and is_token(token_inner)
    # assert token_inner not in [LOOP_BEGIN, LOOP_END]
    v = machine.tape.value()
    if token_inner == INCREMENT:
        machine.tape.set_value(v + 1)
    elif token_inner == DECREMENT:
        machine.tape.set_value(v - 1)
    elif token_inner == ADVANCE:
        machine.tape.advance_by(1)
    elif token_inner == DEVANCE:
        machine.tape.devance_by(1)
    elif token_inner == WRITE:
        machine.write()
    elif token_inner == READ:
        machine.read()


def run(program, stdin, stdout):
    """
    run(program: Parsed, stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    ctx = Context(machine, program)
    for c in ctx:
        machine, _program_full, _i, p = c
        run_token(machine, p)


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
    parser = Parser()
    with tokenize.acquire_from_args(args) as t:
        program = parser.parse(t).collect()
        run(program, sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
