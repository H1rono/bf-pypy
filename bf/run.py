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


def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
        program[:pc], program[pc], program[pc + 1:]
    )


jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['machine'],
                      get_printable_location=get_location)


def mainloop(program, bracket_map, machine):
    pc = 0

    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, machine=machine, program=program,
                                  bracket_map=bracket_map)

        code = program[pc]
        if code == ADVANCE:
            machine.advance_by(1)
        elif code == DEVANCE:
            machine.devance_by(1)
        elif code == INCREMENT:
            machine.inc_by(1)
        elif code == DECREMENT:
            machine.dec_by(1)
        elif code == WRITE:
            # print
            machine.write()
        elif code == READ:
            # read from stdin
            machine.read()
        elif code == LOOP_BEGIN and machine.get() == 0:
            # Skip forward to the matching ]
            pc = bracket_map[pc]
        elif code == LOOP_END and machine.get() != 0:
            # Skip back to the matching [
            pc = bracket_map[pc]

        pc += 1


def run(fp, stdin, stdout):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    program, bm = parse(program_contents)
    machine = Machine(stdin, stdout)
    mainloop(program, bm, machine)


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp, os.fdopen(0) as stdin, os.fdopen(1, 'w') as stdout:
        run(fp.fileno(), stdin, stdout)
    return 0


if __name__ == "__main__":
    entry_point(sys.argv)
