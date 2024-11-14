# instruction kinds
KIND_ONE_CHAR = 1
KIND_SIMPLE_OPS = 2
KIND_MULTIPLY = 3


# Instruction: (kind: kind, val_diffs: ValDiffs, dpos: int, position: Position)
#     where ValDiffs: list[(dpos: int, dval: int)]
#           Position: (begin, end)
def one_char(pc):
    return (KIND_ONE_CHAR, None, 0, (pc, pc + 1))


def simple_ops(val_diffs, dpos, rng):
    return (KIND_SIMPLE_OPS, val_diffs, dpos, rng)


def multiply(val_diffs, rng):
    return (KIND_MULTIPLY, val_diffs, 0, rng)
