from collections import deque

from . import instruction
from .tape import DictTape
from .token import *


def parse_one_char(tokens):
    raw = []
    instructions = []
    for pc, char in tokens.enumerate():
        raw.append(char)
        instr = instruction.one_char(pc)
        instructions.append(instr)
    return "".join(raw), instructions


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
    return (instructions, val_diffs)


def collect_multiply(raw, begin_instr, body_instructions, end_instr, val_diffs):
    i = 0
    tape = DictTape()
    while i < len(body_instructions):
        instr = body_instructions[i]
        kind, rng, dpos, pc_rng = instr
        if kind == instruction.KIND_ONE_CHAR:
            return ((0, 0), False)
        elif kind == instruction.KIND_MULTIPLY:
            nest_instr_begin, nest_instr_end = rng
            i += nest_instr_end - nest_instr_begin
        else:
            vds_begin, vds_end = rng
            tape.accept_val_diffs(val_diffs[vds_begin:vds_end])
            tape.position += dpos
        i += 1
    if tape.position != 0 or tape.data.get(0, 0) != -1:
        return ((0, 0), False)
    _, _, _, begin_pc_rng = begin_instr
    pc_begin, _ = begin_pc_rng
    _, _, _, end_pc_rng = end_instr
    _, pc_end = end_pc_rng
    return ((pc_begin, pc_end), True)


def parse_multiply(raw, simple_ops_instructions, val_diffs):
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
            loop_begin_stack = []
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
        mul_pc_rng, mul_ok = collect_multiply(raw, begin_instr, body_instructions, end_instr, val_diffs)
        if mul_ok:
            mul_instr_begin = begin_at + 1
            mul_instr_end = len(instructions)
            mul_instr_rng = (mul_instr_begin, mul_instr_end)
            mul_instr = instruction.multiply(mul_instr_rng, mul_pc_rng)
            instructions[begin_at] = mul_instr
        else:
            instructions.append(end_instr)
    assert not loop_begin_stack
    return instructions


def parse_bracket_map(raw, instructions):
    bracket_map = {}
    leftstack = []
    pc = 0
    for instr in instructions:
        kind, _, _dpos, pc_rng = instr
        begin, _end = pc_rng
        code = raw[begin]
        if kind != instruction.KIND_ONE_CHAR or code not in BRACKET:
            pc += 1
            continue
        if code == LOOP_BEGIN:
            leftstack.append(pc)
        else: # code == LOOP_END
            left = leftstack.pop()
            right = pc
            bracket_map[left] = right
            bracket_map[right] = left
        pc += 1
    return bracket_map


def parse(tokens):
    raw, one_char_instructions = parse_one_char(tokens)
    simple_ops_instructions, val_diffs = parse_simple_ops(raw, one_char_instructions)
    multiply_instructions = parse_multiply(raw, simple_ops_instructions, val_diffs)
    bracket_map = parse_bracket_map(raw, multiply_instructions)
    metadata = (multiply_instructions, val_diffs, bracket_map)
    return (raw, metadata)


def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp:
        program, metadata = parse(Tokens(fp))
    instructions, val_diffs, bracket_map = metadata
    print "bracket_map:", bracket_map
    instruction_one_char = 0
    instruction_simple_ops = 0
    instruction_multiply = 0
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
        elif kind == instruction.KIND_MULTIPLY:
            instruction_multiply += 1
            i = rng[1] - 1
            print "\t%s %d:%d %s" % (prg, begin, end, str(rng))
        i += 1
    print "ONE_CHAR: %d, SIMPLE_OPS: %d, MULTIPLY: %d" % (instruction_one_char, instruction_simple_ops, instruction_multiply)
    return 0


if __name__ == "__main__":
    from sys import argv
    main(argv)
