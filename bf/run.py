import os
import sys

from instruction import s_rng
from rpython.rlib import jit, types
from rpython.annotator.model import SomeTuple
from rpython.rlib.objectmodel import always_inline, enforceargs, try_inline
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.signature import signature

from .instruction import (
    s_uint, s_instruction, s_instruction_body, s_instructions,
    KIND_ONE_CHAR, KIND_MULTIPLY, KIND_SIMPLE_OPS
)
from .machine import Machine, s_machine
from .parse import parse, s_bracket_map, s_val_diffs, s_metadata
from .token import *


class Context(object):
    def __init__(self, i, mul_end, mul_by):
        self.index = r_uint(i)
        self.multiply_end = r_uint(mul_end)
        self.multiply_by = mul_by
        self.multiply_nests = []

    @try_inline
    def nest(self, mul_end, mul_by):
        p = (self.multiply_end, self.multiply_by)
        self.multiply_nests.append(p)
        self.multiply_end = mul_end
        self.multiply_by = mul_by

    @try_inline
    def pop(self):
        if not self.multiply_nests:
            return
        mul_end, mul_by = self.multiply_nests.pop()
        self.multiply_end = mul_end
        self.multiply_by = mul_by

    @try_inline
    def proceed(self):
        self.index += 1
        if self.index >= self.multiply_end:
            self.pop()


def get_location(context, program, instructions, val_diffs, bracket_map):
    _, _, _, pc_rng = instructions[context.index]
    begin, end = pc_rng
    return "%s_%s_%s" % (
        program[:begin], program_in(program, pc_rng), program[end:]
    )


jitdriver = jit.JitDriver(
    greens=['context', 'program', 'instructions', 'val_diffs', 'bracket_map'],
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
    machine = jit.hint(machine, access_directory=True)

    instructions, val_diffs, bracket_map = metadata
    context = Context(0, len(instructions), 1)
    while context.index < len(instructions):
        jitdriver.jit_merge_point(
            context=context, machine=machine, program=program,
            instructions=instructions, val_diffs=val_diffs, bracket_map=bracket_map,
        )

        kind, rng, dpos, pc_rng = instruction_at(instructions, context.index)
        if kind == KIND_SIMPLE_OPS:
            vds = val_diffs_in(val_diffs, rng)
            machine.tape.accept_val_diffs_multiplied(vds, context.multiply_by)
            machine.tape.advance_by(dpos)
            # instruction_simple_ops(instr, val_diffs, machine)
        elif kind == KIND_ONE_CHAR:
            instr = (rng, dpos, pc_rng)
            context.index = instruction_one_char(context.index, program, instr, bracket_map, machine)
        else: # kind == KIND_MUlTIPLY
            i, mul_end = rng
            mul_by = machine.tape.get()
            context.nest(mul_end, mul_by)
            if mul_by == 0:
                context.index = mul_end - 1
            # context.index = instruction_multiply(instr, val_diffs, instructions, machine)
        context.proceed()


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
