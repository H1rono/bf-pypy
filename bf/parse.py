from .token import MEMBERS, LOOP_BEGIN, LOOP_END


def parse(tokens):
    parsed = []
    bracket_map = {}
    leftstack = []

    for pc, char in tokens.enumerate():
        # assert char in MEMBERS
        parsed.append(char)
        if char == LOOP_BEGIN:
            leftstack.append(pc)
        elif char == LOOP_END:
            left = leftstack.pop()
            right = pc
            bracket_map[left] = right
            bracket_map[right] = left

    return parsed, bracket_map
