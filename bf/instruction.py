# instruction kinds
KIND_ONE_CHAR = 1
KIND_SIMPLE_OPS = 2
KIND_MULTIPLY = 3


# Instruction: (kind: kind, val_diffs: ValDiffs, dpos: int, position: Position)
#     where ValDiffs: list[(dpos: int, dval: int)]
#           Position: (begin, end)
def one_char(pos):
    return (KIND_ONE_CHAR, None, 0, (pos, pos + 1))


def simple_ops(val_diffs, dpos, position):
    return (KIND_SIMPLE_OPS, val_diffs, dpos, position)


def multiply(val_diffs, dpos, position):
    return (KIND_MULTIPLY, val_diffs, dpos, position)