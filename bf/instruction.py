# instruction kinds
KIND_ONE_CHAR = 1
KIND_SIMPLE_OPS = 2
KIND_MULTIPLY = 3


# Instruction(kind: kind, rng: Position, dpos: int, pc_rng: Position)
#     where Position(begin: int, end: int)


def one_char(pc):
    return (KIND_ONE_CHAR, (0, 0), 0, (pc, pc + 1))


# rng: range of val_diffs
def simple_ops(vds_rng, dpos, pc_rng):
    return (KIND_SIMPLE_OPS, vds_rng, dpos, pc_rng)


def multiply(vds_rng, pc_rng):
    return (KIND_MULTIPLY, vds_rng, 0, pc_rng)
