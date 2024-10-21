import sys
from argparse import ArgumentParser

from . import tokenize
from .machine import Machine
from .parse import Parser, Parsed
from .program import Program
from .token import is_token


class LoopContext(object):
    def __init__(self, machine, loop):
        """
        __init__(self, machine: Machine, program: Program.loop)
        """
        assert isinstance(machine, Machine)
        assert isinstance(loop, Program) and loop.kind == Program.KIND_LOOP
        assert loop.loop is not None
        self._machine = machine
        # self._loop: list[Program]
        self._loop = loop.loop
        self._current_index = 0
        # self._current_loop = LoopContext | None
        self._current_loop = None

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
        self._current_index %= len(self._loop)

    def next(self):
        """
        next(self) -> Machine
        """
        if self._current_loop is not None:
            assert isinstance(self._current_loop, LoopContext)
            try:
                m = self._current_loop.next()
            except StopIteration:
                self._current_loop = None
                self._inc_index()
                return self._machine
            else:
                return m
        l = len(self._loop)
        if self._current_index == 0 and self._machine.tape.value == 0:
            raise StopIteration()
        program = self._loop[self._current_index]
        if program.kind == Program.KIND_TOKEN:
            run_token(self._machine, program)
            self._inc_index()
            return self._machine
        assert program.kind == Program.KIND_LOOP
        self._current_loop = LoopContext(self._machine, program)
        return self._machine


class Context(object):
    def __init__(self, machine, program):
        """
        __init__(self, machine: Machine, program: Parsed)
        """
        assert isinstance(machine, Machine)
        assert isinstance(program, Parsed)
        self._machine = machine
        # self._program: Parsed
        self._program = program
        # self._current_loop: LoopContext | None
        self._current_loop = None

    def __iter__(self):
        """
        __iter__(self) -> Self
        # Self: Iterator<Item=Machine>
        """
        return self

    def next(self):
        if self._current_loop is not None:
            assert isinstance(self._current_loop, LoopContext)
            try:
                m = self._current_loop.next()
            except StopIteration:
                self._current_loop = None
                return self._machine
            else:
                return m
        program = self._program.next()
        if program.kind == Program.KIND_TOKEN:
            run_token(self._machine, program)
            return self._machine
        assert program.kind == Program.KIND_LOOP
        self._current_loop = LoopContext(self._machine, program)
        return self._machine


def run_token(machine, token):
    """
    run_token(machine: Machine, token: Program.token) -> None
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    assert isinstance(machine, Machine)
    assert isinstance(token, Program) and token.kind == Program.KIND_TOKEN
    token_inner = token.token
    assert token_inner is not None and is_token(token_inner)
    assert token_inner not in [LOOP_BEGIN, LOOP_END]
    if token_inner == INCREMENT:
        machine.tape.value += 1
    elif token_inner == DECREMENT:
        machine.tape.value -= 1
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
    for _ in ctx:
        pass


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
        program = parser.parse(t)
        run(program, sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
