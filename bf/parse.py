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


def parse(tokens):
    parsed = []
    simple = []
    for pc, char in tokens.enumerate():
        # assert char in MEMBERS
        if char in SIMPLES:
            simple.append((pc, char))
            continue
        if simple:
            raw, instr = parse_simple(simple)
            simple = []
            parsed.append((raw, instr))
        instr = instruction.one_char(pc)
        parsed.append((char, instr))
    raw = "".join([r for r, _ in parsed])
    instructions = [instr for _, instr in parsed]
    bracket_map = parse_bracket_map(raw, instructions)
    metadata = (instructions, bracket_map)
    return (raw, metadata)
