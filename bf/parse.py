from collections import namedtuple

from . import instruction
from .tape import DictTape
from .token import *


def parse_simple_ops(tokens):
    """
    [INCREMENT, DECREMENT, ADVANCE, DEVANCE]
    :param tokens: list[(int, char)]
    :return: (str, list[(int, int)], int, (int, int))
    """
    raw = []
    tape = DictTape()
    begin, _ = tokens[0]
    end = begin
    for i, c in tokens:
        assert c in SIMPLE_OPS
        end = max(end, i)
        raw.append(c)
        if c == INCREMENT:
            tape.inc_by(1)
        elif c == DECREMENT:
            tape.dec_by(1)
        elif c == ADVANCE:
            tape.advance_by(1)
        elif c == DEVANCE:
            tape.devance_by(1)
    val_diffs = [(dp, dv) for dp, dv in tape.data.items()]
    dpos = tape.position
    rng = (begin, end + 1)
    return ("".join(raw), val_diffs, dpos, rng)


def parse_bracket_map(program, instructions):
    bracket_map = {}
    leftstack = []
    pc = 0
    for instr in instructions:
        kind, _vds, _dpos, rng = instr
        begin, _end = rng
        code = program[begin]
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


def parse_loop_to_multiply(val_diffs, begin, body, end):
    if not body:
        return (None, None, (0, 0))
    tape = DictTape()
    raw_acc = ""
    for r, instr in body:
        kind, vds_rng, dpos, _rng = instr
        if kind != instruction.KIND_SIMPLE_OPS:
            return (None, None, (0, 0))
        vds_begin, vds_end = vds_rng
        tape.accept_val_diffs(val_diffs[vds_begin:vds_end])
        tape.advance_by(dpos)
        raw_acc += r
    if tape.position != 0 or tape.data.get(0, 0) != -1:
        return (None, None, (0, 0))
    begin_raw, begin_instr = begin
    begin_i, _ = begin_instr[-1]
    end_raw, end_instr = end
    _, end_i = end_instr[-1]
    raw = begin_raw + raw_acc + end_raw
    val_diffs = [(dp, dv) for dp, dv in tape.data.items()]
    rng = (begin_i, end_i)
    return (raw, val_diffs, rng)


def parse(tokens):
    parsed = []
    simple_ops = []
    loop_begin_stack = []
    val_diffs = []
    for pc, char in tokens.enumerate():
        # assert char in MEMBERS
        if char in SIMPLE_OPS:
            simple_ops.append((pc, char))
            continue
        if simple_ops:
            raw, vds, dp, rng = parse_simple_ops(simple_ops)
            simple_ops = []
            vds_begin = len(val_diffs)
            val_diffs.extend(vds)
            vds_end = len(val_diffs)
            instr = instruction.simple_ops((vds_begin, vds_end), dp, rng)
            parsed.append((raw, instr))
        if char == LOOP_BEGIN or char in IO_OPS:
            if char == LOOP_BEGIN:
                loop_begin_stack.append(len(parsed))
            instr = instruction.one_char(pc)
            parsed.append((char, instr))
            continue
        # char == LOOP_END
        begin_at = loop_begin_stack.pop()
        begin = parsed[begin_at]
        body = parsed[begin_at + 1:]
        end = (char, instruction.one_char(pc))
        raw, vds, rng = parse_loop_to_multiply(val_diffs, begin, body, end)
        if raw is None:
            parsed.append(end)
            continue
        del parsed[begin_at:]
        vds_begin = len(val_diffs)
        val_diffs.extend(vds)
        vds_end = len(val_diffs)
        instr = instruction.multiply((vds_begin, vds_end), rng)
        parsed.append((raw, instr))
    raw = "".join([r for r, _ in parsed])
    instructions = [instr for _, instr in parsed]
    bracket_map = parse_bracket_map(raw, instructions)
    metadata = (instructions, val_diffs, bracket_map)
    return (raw, metadata)


def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1

    with open(filename) as fp:
        program, metadata = parse(Tokens(fp))
    instructions, bracket_map = metadata
    print "bracket_map:", bracket_map
    instruction_one_char = 0
    instruction_simple_ops = 0
    instruction_multiply = 0
    print "instructions:"
    for instr in instructions:
        kind, vds, dpos, rng = instr
        begin, end = rng
        prg = program[begin:end]
        if kind == instruction.KIND_ONE_CHAR:
            instruction_one_char += 1
            print "\t%s\t%d:%d" % (prg, begin, end)
        elif kind == instruction.KIND_SIMPLE_OPS:
            instruction_simple_ops += 1
            print "\t%s %d:%d" % (prg, begin, end), vds, dpos
        elif kind == instruction.KIND_MULTIPLY:
            instruction_multiply += 1
            print "\t%s %d:%d" % (prg, begin, end), vds
    print "ONE_CHAR: %d, SIMPLE_OPS: %d, MULTIPLY: %d" % (instruction_one_char, instruction_simple_ops, instruction_multiply)
    return 0


if __name__ == "__main__":
    from sys import argv
    main(argv)
