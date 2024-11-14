from os import read, write

from .tape import Tape


class Machine(Tape):
    def __init__(self, stdin, stdout):
        Tape.__init__(self)
        self.stdin = stdin.fileno()
        self.stdout = stdout.fileno()

    def read(self):
        buf = read(self.stdin, 1)[0]
        self.set(ord(buf))

    def write(self):
        buf = chr(self.get())
        write(self.stdout, buf)
