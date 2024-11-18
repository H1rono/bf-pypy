import os
import sys

from instruction import s_rng
from rpython.rlib import jit, types
from rpython.rlib.objectmodel import always_inline
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.signature import signature

from .instruction import (
    s_uint, s_instruction, s_instruction_body, s_instructions,
    KIND_ONE_CHAR, KIND_NEST_LOOP, KIND_NEST_MULTIPLY, KIND_SIMPLE_OPS
)
from .machine import Machine, s_machine
from .parse import parse, s_bracket_map, s_val_diffs, s_metadata
from .token import *


def get_location(i, nest_rng, mul_by, nests, program, instructions, val_diffs, bracket_map):
    _, _, _, pc_rng = instructions[i]
    begin, end = pc_rng
    return "%s_%s_%s" % (
        program[:begin], program_in(program, pc_rng), program[end:]
    )


jitdriver = jit.JitDriver(
    greens=['i', 'mul_by', 'nest_rng', 'nests', 'program', 'instructions', 'val_diffs', 'bracket_map'],
    reds=['machine'],
    get_printable_location=get_location,
)

@jit.elidable
@signature(types.str(), s_rng, returns=types.str())
def program_in(program, rng):
    begin, end = rng
    return program[begin:end]


@jit.elidable
@signature(s_instructions, s_uint, returns=s_instruction)
def instruction_at(instructions, i):
    return instructions[i]


@jit.elidable
@signature(s_val_diffs, s_rng, returns=s_val_diffs)
def val_diffs_in(val_diffs, rng):
    begin, end = rng
    return val_diffs[begin:end]


@jit.elidable
@signature(s_bracket_map, s_uint, returns=s_uint)
def corresponding_bracket(map, i):
    return map[i]


@always_inline
@signature(
    s_uint, types.str(), s_instruction_body, s_bracket_map, s_machine,
    returns=s_uint
)
def instruction_one_char(i, program, instr, bracket_map, machine):
    _rng, _dpos, pc_rng = instr
    code = program_in(program, pc_rng)
    # assert code not in SIMPLE_OPS
    if code == WRITE:
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


@signature(types.str(), s_metadata, s_machine, returns=types.none())
def mainloop(program, metadata, machine):
    machine = jit.hint(machine, access_directly=True)

    instructions, val_diffs, bracket_map = metadata
    i = r_uint(0)
    nest_rng = (0, len(instructions))
    mul_by = 1
    nests = []
    while i < len(instructions):
        jitdriver.jit_merge_point(
            i=i, mul_by=mul_by, nest_rng=nest_rng, program=program, nests=nests,
            instructions=instructions, val_diffs=val_diffs, bracket_map=bracket_map,
            machine=machine,
        )

        kind, rng, dpos, pc_rng = instruction_at(instructions, i)
        if kind == KIND_SIMPLE_OPS:
            vds = val_diffs_in(val_diffs, rng)
            machine.tape.accept_val_diffs_multiplied(vds, mul_by)
            machine.tape.advance_by(dpos)
        elif kind == KIND_ONE_CHAR:
            instr = (rng, dpos, pc_rng)
            i = instruction_one_char(i, program, instr, bracket_map, machine)
        else: # kind in [KIND_NEST_MULTIPLY, KIND_NEST_LOOP]
            nests.append((nest_rng, mul_by))
            nest_rng = rng
            mul_by = machine.tape.get()
            if kind == KIND_NEST_LOOP:
                mul_by = min(1, mul_by)
            if mul_by == 0:
                i = r_uint(nest_rng[1] - 1)
        i += 1
        if i >= nest_rng[1] and nests: # getting nest loop out
            if machine.tape.get() == 0:
                nest_rng, mul_by = nests.pop()
            else:
                i = nest_rng[0]


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
