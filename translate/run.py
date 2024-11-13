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

from bf.parse import parse
from bf.tape import Tape
from bf.token import *


def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
        program[:pc], program[pc], program[pc + 1:]
    )


jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['tape'],
                      get_printable_location=get_location)


def mainloop(program, bracket_map):
    pc = 0
    tape = Tape()

    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program,
                                  bracket_map=bracket_map)

        code = program[pc]
        if code == ADVANCE:
            tape.advance_by(1)
        elif code == DEVANCE:
            tape.devance_by(1)
        elif code == INCREMENT:
            tape.inc_by(1)
        elif code == DECREMENT:
            tape.dec_by(1)
        elif code == WRITE:
            # print
            os.write(1, chr(tape.get()))
        elif code == READ:
            # read from stdin
            tape.set(ord(os.read(0, 1)[0]))
        elif code == LOOP_BEGIN and tape.get() == 0:
            # Skip forward to the matching ]
            pc = bracket_map[pc]
        elif code == LOOP_END and tape.get() != 0:
            # Skip back to the matching [
            pc = bracket_map[pc]
        pc += 1


def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program, bm = parse(program_contents)
    mainloop(program, bm)


def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    run(os.open(filename, os.O_RDONLY, 0777))
    return 0


def target(*args):
    return entry_point, None


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


if __name__ == "__main__":
    entry_point(sys.argv)
