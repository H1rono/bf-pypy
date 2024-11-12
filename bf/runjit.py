import sys
from argparse import ArgumentParser

from rpython.rlib.jit import JitDriver

from . import tokenize
from .machine import Machine
from .parse import parse
from .run import run_token, Frames


_jit_driver = JitDriver(
    greens=["pos", "program", "token"],
    reds=["machine"],
    is_recursive=True
)


def _iteration(frame):
    pos, machine, program = frame
    token = program.tokens[pos.at]
    _jit_driver.jit_merge_point(pos=pos, program=program, token=token, machine=machine)
    run_token(pos, machine, token, program)


def run(program, stdin, stdout):
    """
    run(program: ParseResult, stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    frames = Frames(machine, program)
    for f in frames:
        _iteration(f)


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
