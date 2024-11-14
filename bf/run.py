import os
import sys

from rpython.rlib import jit

from .instruction import KIND_ONE_CHAR, KIND_MULTIPLY, KIND_SIMPLE_OPS
from .machine import Machine
from .parse import parse
from .token import *


def get_location(i, program, instructions, val_diffs, bracket_map):
    _, _, _, pc_rng = instructions[i]
    begin, end = pc_rng
    return "%s_%s_%s" % (
        program[:begin], program[begin:end], program[end:]
    )


jitdriver = jit.JitDriver(
    greens=['i', 'program', 'instructions', 'val_diffs', 'bracket_map'],
    reds=['machine'],
    get_printable_location=get_location,
)


def instruction_at(instructions, i):
    return instructions[i]


def val_diffs_in(val_diffs, rng):
    begin, end = rng
    return val_diffs[begin:end]


def corresponding_bracket(map, i):
    return map[i]


def instruction_one_char(i, program, instr, _val_diffs, bracket_map, machine):
    _vds, _dpos, pc_rng = instr
    begin, _end = pc_rng
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
        return corresponding_bracket(bracket_map, i)
    elif code == LOOP_END and machine.get() != 0:
        # Skip back to the matching [
        return corresponding_bracket(bracket_map, i)
    return i


def instruction_simple_ops(_i, _program, instr, val_diffs, _bracket_map, machine):
    vds_rng, dpos, _pc_rng = instr
    vds = val_diffs_in(val_diffs, vds_rng)
    machine.accept_val_diffs(vds)
    machine.advance_by(dpos)


def instruction_multiply(_i, _program, instr, val_diffs, _bracket_map, machine):
    vds_rng, _dpos, _pc_rng = instr
    vds = val_diffs_in(val_diffs, vds_rng)
    machine.mul_accept_val_diffs(vds)


def mainloop(program, metadata, machine):
    instructions, val_diffs, bracket_map = metadata
    i = 0

    while i < len(instructions):
        jitdriver.jit_merge_point(
            i=i, machine=machine, program=program,
            instructions=instructions, val_diffs=val_diffs, bracket_map=bracket_map,
        )

        kind, rng, dpos, pc_rng = instruction_at(instructions, i)
        instr = (rng, dpos, pc_rng)
        if kind == KIND_SIMPLE_OPS:
            instruction_simple_ops(i, program, instr, val_diffs, bracket_map, machine)
        elif kind == KIND_ONE_CHAR:
            i = instruction_one_char(i, program, instr, val_diffs, bracket_map, machine)
        elif kind == KIND_MULTIPLY:
            instruction_multiply(i, program, instr, val_diffs, bracket_map, machine)
        i += 1


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
