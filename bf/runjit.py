import sys
from argparse import ArgumentParser

from rpython.rlib.jit import JitDriver

from . import tokenize
from .machine import Machine
from .parse import Parser
from .program import Program
from .token import is_token


def _get_location(i, is_loop, p, program):
    """
    _get_location(i: int, is_loop: bool, p: Program, program: list[Program], machine: Machine) -> str
    """
    # assert isinstance(i, int)
    # assert isinstance(is_loop, bool)
    # assert isinstance(p, Program)
    # assert isinstance(program, list)
    # assert isinstance(machine, Machine)
    prev = program[:i]
    prev_str = ""
    for pr in prev:
        prev_str += pr.raw_str()
    rest = program[i + 1:0]
    rest_str = ""
    for re in rest:
        rest_str += re.raw_str()
    return "%s_%s_%s" % (
        prev_str,
        p.raw_str(),
        rest_str,
    )


def run_token(machine, token):
    """
    run_token(machine: Machine, token: Program.token) -> None
    """
    from .token import INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END

    # assert isinstance(machine, Machine)
    # assert isinstance(token, Program) and token.kind == Program.KIND_TOKEN
    token_inner = token.token
    # assert token_inner is not None and is_token(token_inner)
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


_jit_driver = JitDriver(
    greens=["i", "is_loop", "p", "program"],
    reds=["machine"],
    get_printable_location=_get_location,
    is_recursive=True,
)


def run_inner(program, machine, is_loop=False):
    """
    run_inner(program: list[Program], machine: Machine, is_loop: bool) -> None
    """
    i = 0
    while i < len(program):
        if is_loop and i == 0 and machine.tape.value() == 0:
            return
        p = program[i]
        _jit_driver.jit_merge_point(i=i, is_loop=is_loop, p=p, program=program, machine=machine)
        if p.kind == Program.KIND_TOKEN:
            # assert is_token(p.token)
            run_token(machine, p)
        else:
            # assert p.kind == Program.KIND_LOOP and p.loop is not None
            run_inner(p.loop, machine, is_loop=True)
        i += 1
        if is_loop:
            i %= len(program)
        # _jit_driver.can_enter_jit(i=i, is_loop=is_loop, p=p, program=program, machine=machine)


def run(program, stdin, stdout):
    """
    run(program: list[Program], stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    run_inner(program, machine, is_loop=False)


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
