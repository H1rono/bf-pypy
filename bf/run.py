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


@jit.elidable
def instruction_at(instructions, i):
    return instructions[i]


@jit.elidable
def val_diffs_in(val_diffs, rng):
    begin, end = rng
    return val_diffs[begin:end]


@jit.elidable
def corresponding_bracket(map, i):
    return map[i]


def instruction_one_char(i, program, instr, _val_diffs, bracket_map, machine):
    _rng, _dpos, pc_rng = instr
    begin, _end = pc_rng
    code = program[begin]
    if code == ADVANCE:
        machine.tape.advance_by(1)
    elif code == DEVANCE:
        machine.tape.devance_by(1)
    elif code == INCREMENT:
        machine.tape.inc_by(1)
    elif code == DECREMENT:
        machine.tape.dec_by(1)
    elif code == WRITE:
        machine.write()
    elif code == READ:
        machine.read()
    elif code == LOOP_BEGIN and machine.tape.get() == 0:
        # Skip forward to the matching ]
        return corresponding_bracket(bracket_map, i)
    elif code == LOOP_END and machine.tape.get() != 0:
        # Skip back to the matching [
        return corresponding_bracket(bracket_map, i)
    return i


def instruction_simple_ops(_i, _program, instr, val_diffs, _bracket_map, machine):
    vds_rng, dpos, _pc_rng = instr
    vds = val_diffs_in(val_diffs, vds_rng)
    machine.tape.accept_val_diffs(vds)
    machine.tape.advance_by(dpos)


def instruction_multiply(instr, val_diffs, instructions, machine):
    instr_rng, _, _ = instr
    i, instr_end = instr_rng
    mul_by = machine.tape.get()
    if mul_by == 0:
        return instr_end - 1
    while i < instr_end:
        child_instr = instruction_at(instructions, i)
        c_kind, c_rng, c_dpos, c_pc_rng = child_instr
        assert c_kind != KIND_ONE_CHAR
        if c_kind == KIND_SIMPLE_OPS:
            vds = val_diffs_in(val_diffs, c_rng)
            machine.tape.accept_val_diffs_multiplied(vds, mul_by)
            machine.tape.advance_by(c_dpos)
        elif c_kind == KIND_MULTIPLY:
            c_instr = (c_rng, c_dpos, c_pc_rng)
            i = instruction_multiply(c_instr, val_diffs, instructions, machine)
        i += 1
    assert machine.tape.get() == 0
    return instr_end - 1


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
            i = instruction_multiply(instr, val_diffs, instructions, machine)
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
    stdin = os.fdopen(0, 'r')
    stdout = os.fdopen(1, 'w')
    run(program, metadata, stdin, stdout)
    return 0


if __name__ == "__main__":
    entry_point(sys.argv)
