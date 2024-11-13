from .token import *


def parse_simple(tokens):
    """
    [INCREMENT, DECREMENT, ADVANCE, DEVANCE]
    :param tokens:
    :return:
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
    return ("".join(raw), vds, dpos, (begin, end + 1))


def parse(tokens):
    parsed = []
    bracket_map = {}
    leftstack = []
    simple = []
    i = 0

    for pc, char in tokens.enumerate():
        # assert char in MEMBERS
        if char in SIMPLES:
            simple.append((pc, char))
            continue
        if simple:
            code = parse_simple(simple)
            simple = []
            parsed.append(code)
            i += 1
        code = (char, None, 0, (pc, pc + 1))
        if char == LOOP_BEGIN:
            leftstack.append(i)
        elif char == LOOP_END:
            left = leftstack.pop()
            right = i
            bracket_map[left] = right
            bracket_map[right] = left
        parsed.append(code)
        i += 1

    raw = [c for c, _, _, _ in parsed]
    instructions = [(vds, dpos, rng) for _, vds, dpos, rng in parsed]
    return ("".join(raw), instructions, bracket_map)
