import os
import sys

from rpython.rlib import jit

from .instruction import KIND_ONE_CHAR, KIND_MULTIPLY, KIND_SIMPLE_OPS
from .machine import Machine
from .parse import parse
from .token import *


def get_location(pc, program, instructions, bracket_map):
    _, _, _, rng = instructions[pc]
    begin, end = rng
    return "%s_%s_%s" % (
        program[:begin], program[begin:end], program[end:]
    )


jitdriver = jit.JitDriver(
    greens=['pc', 'program', 'instructions', 'bracket_map'],
    reds=['machine'],
    get_printable_location=get_location,
)


def instruction_at(instructions, i):
    return instructions[i]


def corresponding_bracket(map, i):
    return map[i]


def instruction_one_char(pc, program, instr, bracket_map, machine):
    _vds, _dpos, rng = instr
    begin, _end = rng
    code = program[begin]
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
        return corresponding_bracket(bracket_map, pc)
    elif code == LOOP_END and machine.get() != 0:
        # Skip back to the matching [
        return corresponding_bracket(bracket_map, pc)
    return pc


def instruction_simple_ops(_pc, _program, instr, _bracket_map, machine):
    vds, dpos, _rng = instr
    machine.accept_val_diffs(vds)
    machine.advance_by(dpos)


def instruction_multiply(_pc, _program, instr, _bracket_map, machine):
    vds, _dpos, _rng = instr
    machine.mul_accept_val_diffs(vds)


def mainloop(program, metadata, machine):
    instructions, bracket_map = metadata
    pc = 0

    while pc < len(instructions):
        jitdriver.jit_merge_point(
            pc=pc, machine=machine, program=program,
            instructions=instructions, bracket_map=bracket_map,
        )

        kind, vds, dpos, rng = instruction_at(instructions, pc)
        instr = (vds, dpos, rng)
        if kind == KIND_SIMPLE_OPS:
            instruction_simple_ops(pc, program, instr, bracket_map, machine)
        elif kind == KIND_ONE_CHAR:
            pc = instruction_one_char(pc, program, instr, bracket_map, machine)
        elif kind == KIND_MULTIPLY:
            instruction_multiply(pc, program, instr, bracket_map, machine)
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
