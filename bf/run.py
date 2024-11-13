import os
import sys

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver
except ImportError:
    class JitDriver(object):
        def __init__(self, **kw): pass

        def jit_merge_point(self, **kw): pass

        def can_enter_jit(self, **kw): pass

from .machine import Machine
from .parse import parse
from .token import *


def get_location(pc, program, metadata):
    instructions, _ = metadata
    _, _, pos = instructions[pc]
    begin, end = pos
    return "%s_%s_%s" % (
        program[:begin], program[begin:end], program[end:]
    )


jitdriver = JitDriver(greens=['pc', 'program', 'instructions', 'bracket_map'], reds=['machine'])


def mainloop(program, metadata, machine):
    instructions, bracket_map = metadata
    pc = 0

    while pc < len(instructions):
        jitdriver.jit_merge_point(
            pc=pc, machine=machine, program=program,
            instructions=instructions, bracket_map=bracket_map,
        )

        vds, dpos, rng = instructions[pc]
        if vds is not None:
            machine.accept_val_diffs(vds)
            machine.advance_by(dpos)
            pc += 1
            continue
        begin, end = rng
        assert end - begin == 1
        code = program[begin:end]
        if code == ADVANCE:
            machine.advance_by(1)
        elif code == DEVANCE:
            machine.devance_by(1)
        elif code == INCREMENT:
            machine.inc_by(1)
        elif code == DECREMENT:
            machine.dec_by(1)
        elif code == WRITE:
            machine.write()
        elif code == READ:
            machine.read()
        elif code == LOOP_BEGIN and machine.get() == 0:
            # Skip forward to the matching ]
            pc = bracket_map[pc]
        elif code == LOOP_END and machine.get() != 0:
            # Skip back to the matching [
            pc = bracket_map[pc]

        pc += 1


def run(program, metadata, stdin, stdout):
    machine = Machine(stdin, stdout)
    mainloop(program, metadata, machine)


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp:
        program, metadata = parse(Tokens(fp))
    with os.fdopen(0, 'r') as stdin, os.fdopen(1, 'w') as stdout:
        run(program, metadata, stdin, stdout)
    return 0


if __name__ == "__main__":
    entry_point(sys.argv)
