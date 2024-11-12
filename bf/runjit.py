import sys
from argparse import ArgumentParser

from rpython.rlib.jit import JitDriver

from . import tokenize
from .machine import Machine
from .parse import parse, ParseResult
from .run import run_token, Frames


def _get_printable_location(pos, program, token):
    # assert isinstance(program, ParseResult)
    raw, token_pos = token
    begin, end = token_pos
    return "%s_%s_%s" % (
        program.raw[:begin],
        raw,
        program.raw[end:],
    )


_jit_driver = JitDriver(
    greens=["pos", "program", "token"],
    reds=["machine"],
    get_printable_location=_get_printable_location,
)


def _iteration(frame):
    pos, machine, program = frame
    token = program.tokens[pos].as_tuple()
    _jit_driver.jit_merge_point(pos=pos, program=program, token=token, machine=machine)
    npos = run_token(pos, machine, token, program)
    return npos


def run(program, stdin, stdout):
    """
    run(program: ParseResult, stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    frames = Frames(machine, program)
    for f in frames:
        p = _iteration(f)
        frames.pos = p


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
