from collections import namedtuple

from . import instruction
from .token import *


def parse_simple(tokens):
    """
    [INCREMENT, DECREMENT, ADVANCE, DEVANCE]
    :param tokens: list[(int, char)]
    :return: (str, list[(int, int)], int, (int, int))
    """
    dpos = 0
    raw = []
    val_diffs = {}
    begin, _ = tokens[0]
    end = begin
    for i, c in tokens:
        assert c in SIMPLES
        end = max(end, i)
        raw.append(c)
        if c == INCREMENT:
            val_diffs[dpos] = val_diffs.get(dpos, 0) + 1
        elif c == DECREMENT:
            val_diffs[dpos] = val_diffs.get(dpos, 0) - 1
        elif c == ADVANCE:
            dpos += 1
        elif c == DEVANCE:
            dpos -= 1
    vds = [(k, v) for k, v in val_diffs.items()]
    instr = instruction.simple_ops(vds, dpos, (begin, end + 1))
    return ("".join(raw), instr)


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


def parse_loop_to_multiply(begin, body, end):
    if not body:
        return None
    dpos_acc = 0
    val_diffs_acc = {}
    raw_acc = ""
    for r, instr in body:
        kind, vds, dpos, _rng = instr
        if kind != instruction.KIND_SIMPLE_OPS:
            return None
        for dp, dv in vds:
            pos = dpos_acc + dp
            val_diffs_acc[pos] = val_diffs_acc.get(pos, 0) + dv
        dpos_acc += dpos
        raw_acc += r
    if dpos_acc != 0 or val_diffs_acc[0] != -1:
        return None
    begin_raw, begin_instr = begin
    begin_i, _ = begin_instr[-1]
    end_raw, end_instr = end
    _, end_i = end_instr[-1]
    raw = begin_raw + raw_acc + end_raw
    val_diffs = [(dp, dv) for dp, dv in val_diffs_acc.items()]
    rng = (begin_i, end_i)
    instr = instruction.multiply(val_diffs, rng)
    return [(raw, instr)]


def parse(tokens):
    parsed = []
    simple = []
    loop_begin_stack = []
    for pc, char in tokens.enumerate():
        # assert char in MEMBERS
        if char in SIMPLES:
            simple.append((pc, char))
            continue
        if simple:
            raw, instr = parse_simple(simple)
            simple = []
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
        instr = instruction.one_char(pc)
        end = (char, instr)
        parsed_mul = parse_loop_to_multiply(begin, body, end)
        if parsed_mul is not None:
            del parsed[begin_at:]
            parsed.extend(parsed_mul)
        else:
            parsed.append(end)
    raw = "".join([r for r, _ in parsed])
    instructions = [instr for _, instr in parsed]
    bracket_map = parse_bracket_map(raw, instructions)
    metadata = (instructions, bracket_map)
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
    print "instructions:"
    for instr in instructions:
        kind, vds, dpos, rng = instr
        begin, end = rng
        prg = program[begin:end]
        if kind == instruction.KIND_ONE_CHAR:
            print "\t%s\t%d:%d" % (prg, begin, end)
        elif kind == instruction.KIND_SIMPLE_OPS:
            print "\t%s %d:%d" % (prg, begin, end), vds
        elif kind == instruction.KIND_MULTIPLY:
            print "\t%s %d:%d" % (prg, begin, end), vds
    return 0


if __name__ == "__main__":
    from sys import argv
    main(argv)
