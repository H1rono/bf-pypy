from os import read, write

from .tape import Tape


class Machine(Tape):
    def __init__(self, stdin, stdout):
        Tape.__init__(self)
        self.stdin = stdin
        self.stdout = stdout

    def read(self):
        # buf = read(self.stdin, 1)[0]
        buf = self.stdin.read(1)[0]
        self.set(ord(buf))

    def write(self):
        buf = chr(self.get())
        # write(self.stdout, buf)
        self.stdout.write(buf)
