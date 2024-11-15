from rpython.annotator.model import SomeInteger, SomeTuple
from rpython.rlib import types
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.signature import signature


# instruction kinds
KIND_ONE_CHAR = r_uint(1)
KIND_SIMPLE_OPS = r_uint(2)
KIND_MULTIPLY = r_uint(3)


s_uint = SomeInteger(knowntype=r_uint)
s_rng = SomeTuple((s_uint, s_uint))
s_instruction = SomeTuple((s_uint, s_rng, types.int(), s_rng))


# Instruction(kind: kind, rng: Position, dpos: int, pc_rng: Position)
#     where Position(begin: int, end: int)


@signature(s_uint, returns=s_instruction)
def one_char(pc):
    return (KIND_ONE_CHAR, (0, 0), 0, (pc, pc + 1))


# rng: range of val_diffs
@signature(s_rng, types.int(), s_rng, returns=s_instruction)
def simple_ops(vds_rng, dpos, pc_rng):
    return (KIND_SIMPLE_OPS, vds_rng, dpos, pc_rng)


# rng: range of child-instructions
@signature(s_rng, s_rng, returns=s_instruction)
def multiply(instr_rng, pc_rng):
    return (KIND_MULTIPLY, instr_rng, 0, pc_rng)
