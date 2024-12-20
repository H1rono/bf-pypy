from instruction import KIND_NEST_LOOP, KIND_NEST_MULTIPLY
from rpython.annotator import model, dictdef, listdef
from rpython.rlib import types
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.signature import signature

from . import instruction
from .instruction import s_uint, s_rng, s_instruction, s_instructions
from .tape import DictTape
from .token import *


s_val_diffs_item = model.SomeTuple((types.int(), types.int()))
s_val_diffs = model.SomeList(listdef.ListDef(None, s_val_diffs_item))
s_metadata = model.SomeTuple((s_instructions, s_val_diffs))
s_parse_result = model.SomeTuple((types.str(), s_metadata))


@signature(s_tokens, returns=model.SomeTuple((types.str(), s_instructions)))
def parse_one_char(tokens):
    raw = []
    instructions = []
    for pc, char in tokens.enumerate():
        raw.append(char)
        instr = instruction.one_char(pc)
        instructions.append(instr)
    return "".join(raw), instructions


@signature(types.str(), returns=model.SomeTuple((s_val_diffs, types.int())))
def collect_simple_ops(raw):
    tape = DictTape()
    for char in raw:
        assert char in SIMPLE_OPS
        if char == INCREMENT:
            tape.inc_by(1)
        elif char == DECREMENT:
            tape.dec_by(1)
        elif char == ADVANCE:
            tape.advance_by(1)
        elif char == DEVANCE:
            tape.devance_by(1)
    val_diffs = tape.collect_val_diffs()
    dpos = tape.position
    return (val_diffs, dpos)


@signature(types.str(), s_instructions, returns=model.SomeTuple((s_instructions, s_val_diffs)))
def parse_simple_ops(raw, one_char_instructions):
    instructions = []
    val_diffs = []
    simple_ops_begin = []
    for instr in one_char_instructions:
        _kind, _, _, pc_rng = instr
        # assert kind == instruction.KIND_ONE_CHAR
        pc, _ = pc_rng
        char = raw[pc]
        # assert char in MEMBERS
        if char in SIMPLE_OPS:
            if not simple_ops_begin:
                simple_ops_begin.append(pc)
            continue
        if simple_ops_begin:
            left = simple_ops_begin.pop()
            right = pc
            vds, dpos = collect_simple_ops(raw[left:right])
            vds_begin = len(val_diffs)
            val_diffs.extend(vds)
            vds_end = len(val_diffs)
            vds_rng = (vds_begin, vds_end)
            simple_ops_instr = instruction.simple_ops(vds_rng, dpos, (left, right))
            instructions.append(simple_ops_instr)
        instructions.append(instr)
    # workaround to pass translation with this @signature
    return ([i for i in instructions], [vd for vd in val_diffs])


# @signature(
#     types.str(), s_instructions, s_val_diffs,
#     returns=types.instance(DictTape, can_be_None=True),
# )
def emulate_multiply(raw, body_instructions, val_diffs):
    i = 0
    tape = DictTape()
    while i < len(body_instructions):
        instr = body_instructions[i]
        kind, rng, dpos, pc_rng = instr
        if kind == instruction.KIND_ONE_CHAR:
            return None
        elif kind == instruction.KIND_SIMPLE_OPS:
            vds_begin, vds_end = rng
            tape.accept_val_diffs(val_diffs[vds_begin:vds_end])
            tape.position += dpos
            i += 1
            continue
        # kind == instruction.KIND_MULTIPLY
        instr_begin = i + 1
        instr_end = r_uint(rng[1] - rng[0]) + instr_begin
        child_tape = emulate_multiply(raw, body_instructions[instr_begin:instr_end], val_diffs)
        if child_tape is None:
            return None
        for dp, dv in child_tape.data.items():
            pos = dp + tape.position
            if pos in tape.data:
                return None
            tape.data[pos] = dv
        i = instr_end
    if tape.position != 0:
        return None
    return tape


# @signature(
#     types.str(), s_instruction, s_instructions, s_instruction, s_val_diffs,
#     returns=model.SomeTuple((s_uint, s_rng)),
# )
def collect_nest(raw, begin_instr, body_instructions, end_instr, val_diffs):
    tape = emulate_multiply(raw, body_instructions, val_diffs)
    if tape is None or tape.position != 0 or tape.data.get(0, 0) != -1:
        kind = KIND_NEST_LOOP
    else:
        kind = KIND_NEST_MULTIPLY
    _, _, _, begin_pc_rng = begin_instr
    pc_begin, _ = begin_pc_rng
    _, _, _, end_pc_rng = end_instr
    _, pc_end = end_pc_rng
    return (kind, (pc_begin, pc_end))


@signature(types.str(), s_instructions, s_val_diffs, returns=s_instructions)
def parse_nests(raw, simple_ops_instructions, val_diffs):
    instructions = []
    loop_begin_stack = []
    for instr in simple_ops_instructions:
        kind, rng, dpos, pc_rng = instr
        if kind != instruction.KIND_ONE_CHAR:
            instructions.append(instr)
            continue
        pc, _ = pc_rng
        char = raw[pc]
        if char in IO_OPS:
            # loop_begin_stack = []
            instructions.append(instr)
            continue
        elif char == LOOP_BEGIN:
            loop_begin_stack.append(len(instructions))
            instructions.append(instr) # placeholder
            continue
        assert char == LOOP_END
        if not loop_begin_stack:
            instructions.append(instr)
            continue
        begin_at = loop_begin_stack.pop()
        begin_instr = instructions[begin_at]
        body_instructions = instructions[begin_at + 1:]
        end_instr = instr
        nest_kind, nest_pc_rng = collect_nest(raw, begin_instr, body_instructions, end_instr, val_diffs)
        nest_instr_begin = begin_at + 1
        nest_instr_end = len(instructions)
        nest_instr_rng = (nest_instr_begin, nest_instr_end)
        nest_instr = (
            instruction.nest_multiply(nest_instr_rng, nest_pc_rng)
            if nest_kind == KIND_NEST_MULTIPLY else
            instruction.nest_loop(nest_instr_rng, nest_pc_rng)
        )
        instructions[begin_at] = nest_instr
    assert not loop_begin_stack
    # workaround to pass translation with this @signature
    return [i for i in instructions]


@signature(s_tokens, returns=s_parse_result)
def parse(tokens):
    raw, one_char_instructions = parse_one_char(tokens)
    simple_ops_instructions, val_diffs = parse_simple_ops(raw, one_char_instructions)
    nest_instructions = parse_nests(raw, simple_ops_instructions, val_diffs)
    metadata = (nest_instructions, val_diffs)
    return (raw, metadata)


def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp:
        program, metadata = parse(Tokens(fp))
    instructions, val_diffs = metadata
    instruction_one_char = 0
    instruction_simple_ops = 0
    instruction_nest = 0
    print "instructions:"
    i = 0
    while i < len(instructions):
        kind, rng, dpos, pc_rng = instructions[i]
        begin, end = pc_rng
        prg = program[begin:end]
        if kind == instruction.KIND_ONE_CHAR:
            instruction_one_char += 1
            print "\t%s\t%d:%d" % (prg, begin, end)
        elif kind == instruction.KIND_SIMPLE_OPS:
            instruction_simple_ops += 1
            vds_begin, vds_end = rng
            vds = val_diffs[vds_begin:vds_end]
            print "\t%s %d:%d" % (prg, begin, end), vds, dpos
        elif kind == instruction.KIND_NEST_MULTIPLY:
            instruction_nest += 1
            i = rng[1] - 1
            print "\t%s %d:%d %s" % (prg, begin, end, str(rng))
        elif kind == instruction.KIND_NEST_LOOP:
            instruction_nest += 1
            i = rng[1] - 1
            print "\t%s %d:%d %s" % (prg, begin, end, str(rng))
        i += 1
    print "ONE_CHAR: %d, SIMPLE_OPS: %d, NEST: %d" % (instruction_one_char, instruction_simple_ops, instruction_nest)
    return 0


if __name__ == "__main__":
    from sys import argv
    main(argv)
