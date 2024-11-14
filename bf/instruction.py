# instruction kinds
KIND_ONE_CHAR = 1
KIND_SIMPLE_OPS = 2
KIND_MULTIPLY = 3


# Instruction: (kind: kind, vds_rng: ValDiffsPosition, dpos: int, rng: Position)
#     where ValDiffsPosition: (begin: int, end: int
#           Position: (begin: int, end: int)
def one_char(pc):
    return (KIND_ONE_CHAR, (0, 0), 0, (pc, pc + 1))


def simple_ops(vds_rng, dpos, rng):
    return (KIND_SIMPLE_OPS, vds_rng, dpos, rng)


def multiply(vds_rng, rng):
    return (KIND_MULTIPLY, vds_rng, 0, rng)
