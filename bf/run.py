import sys
from argparse import ArgumentParser

from rpython.rlib.jit import elidable

from . import tokenize, program as bf_program
from .machine import Machine
from .parse import Parser
from .program import Program
from .token import is_token, LOOP_BEGIN, LOOP_END


class NestContext(object):
    __slots__ = ["_loop", "_current_index"]

    @elidable
    def __init__(self, loop):
        """
        __init__(self, loop: list[Program])
        """
        # assert isinstance(loop, list)
        self._loop = loop
        self._current_index = 0

    def next_with(self, machine):
        """
        next_with(self, machine: Machine) -> (list[Program], i, Program)
        """
        try:
            program = self._loop[self._current_index]
        except IndexError:
            raise StopIteration()
        self._current_index += 1
        i = self._current_index
        vv = machine.tape.value() != 0
        if program.token == LOOP_END and vv:
            self._current_index = 0
        elif program.token == LOOP_BEGIN and not vv:
            raise StopIteration()
        return (self._loop, i, program)


class Context(object):
    __slots__ = ["_machine", "_program", "_current_index", "_nest_loops"]

    def __init__(self, machine, program):
        """
        __init__(self, machine: Machine, program: list[Program])
        """
        assert isinstance(machine, Machine)
        assert isinstance(program, list)
        self._machine = machine
        self._program = program
        self._current_index = 0
        self._nest_loops = []

    def __iter__(self):
        """
        __iter__(self) -> Self
        # Self: Iterator<Item=(Machine, list[Program], int, Program.token)>
        """
        return self

    def _inc_index(self):
        """
        _inc_index(self) -> int
        """
        self._current_index += 1
        return self._current_index

    def next(self):
        try:
            while True:
                loop = self._nest_loops.pop(-1)
                assert isinstance(loop, NestContext)
                try:
                    ll, i, program = loop.next_with(self._machine)
                except StopIteration:
                    continue
                self._nest_loops.append(loop)
                break
        except IndexError:
            ll = self._program
            try:
                program = self._program[self._current_index]
            except IndexError:
                raise StopIteration()
            i = self._inc_index()
        if program.kind == Program.KIND_TOKEN:
            return (self._machine, ll, i, program)
        nest = NestContext(program.loop)
        self._nest_loops.append(nest)
        return (self._machine, program.loop, i, bf_program.token(LOOP_BEGIN))


def run_token(machine, token):
    """
    run_token(machine: Machine, token: Token) -> None
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    assert is_token(token)
    # assert token not in [LOOP_BEGIN, LOOP_END]
    v = machine.tape.value()
    if token == INCREMENT:
        machine.tape.set_value(v + 1)
    elif token == DECREMENT:
        machine.tape.set_value(v - 1)
    elif token == ADVANCE:
        machine.tape.advance_by(1)
    elif token == DEVANCE:
        machine.tape.devance_by(1)
    elif token == WRITE:
        machine.write()
    elif token == READ:
        machine.read()


def run(program, stdin, stdout):
    """
    run(program: Parsed, stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    ctx = Context(machine, program)
    for c in ctx:
        machine, _program_full, _i, p = c
        run_token(machine, p.token)


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
