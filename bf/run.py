import sys
from argparse import ArgumentParser

from . import tokenize
from .machine import Machine
from .parse import Parser, Parsed
from .program import Program
from .token import is_token


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


def run_loop(machine, loop):
    """
    run_loop(machine: Machine, loop: Program.loop) -> None
    """
    assert isinstance(machine, Machine)
    assert isinstance(loop, Program) and loop.kind == Program.KIND_LOOP
    loop_inner = loop.loop
    while True:
        for p in loop_inner:
            if p.kind == Program.KIND_TOKEN:
                run_token(machine, p)
                continue
            assert p.kind == Program.KIND_LOOP
            run_loop(machine, p)
        if machine.tape.value == 0:
            break


def run(program, stdin, stdout):
    """
    run(program: Parsed, stdin: File, stdout: File) -> None
    """
    machine = Machine(stdin, stdout)
    for p in program:
        # print "run %s" % p.to_str()
        if p.kind == Program.KIND_TOKEN:
            run_token(machine, p)
            continue
        assert p.kind == Program.KIND_LOOP
        run_loop(machine, p)


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
