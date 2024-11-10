import sys
from argparse import ArgumentParser

from rpython.rlib.jit import JitDriver

from . import tokenize, run as bf_run
from .machine import Machine
from .parse import Parser
from .program import Program
from .token import is_token


_jit_driver = JitDriver(
    greens=["i", "program", "token"],
    reds=["machine"],
)


def _iteration(machine, program, i, token):
    """
    _iteration(machine: Machine, program: list[Program], i: int, token: Program.token) -> None
    """
    _jit_driver.jit_merge_point(i=i, program=program, token=token, machine=machine)
    bf_run.run_token(machine, token)


def run_inner(program, machine):
    """
    run_inner(program: list[Program], machine: Machine, is_loop: bool) -> None
    """
    ctx = bf_run.Context(machine, program)
    for c in ctx:
        machine, program, i, token = c
        _iteration(machine, program, i, token)


def run(program, stdin, stdout):
    """
    run(program: list[Program], stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    run_inner(program, machine)


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
