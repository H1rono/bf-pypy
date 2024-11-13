from os import read, write

from .tape import Tape


class Machine(Tape):
    def __init__(self, stdin, stdout):
        Tape.__init__(self)
        self.stdin = stdin.fileno()
        self.stdout = stdout.fileno()

    def accept_val_diffs(self, val_diffs):
        for dpos, dval in val_diffs:
            pos = self.position + dpos
            ext_len = pos - len(self.thetape)
            if ext_len >= 0:
                self.thetape.extend([0] * (ext_len + 1))
            self.thetape[pos] += dval

    def read(self):
        buf = read(self.stdin, 1)[0]
        self.set(ord(buf))

    def write(self):
        buf = chr(self.get())
        write(self.stdout, buf)
