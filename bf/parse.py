from .token import MEMBERS, LOOP_BEGIN, LOOP_END


def parse(program):
    parsed = []
    bracket_map = {}
    leftstack = []

    pc = 0
    for char in program:
        if char not in MEMBERS:
            continue

        parsed.append(char)
        if char == LOOP_BEGIN:
            leftstack.append(pc)
        elif char == LOOP_END:
            left = leftstack.pop()
            right = pc
            bracket_map[left] = right
            bracket_map[right] = left
        pc += 1

    return "".join(parsed), bracket_map
