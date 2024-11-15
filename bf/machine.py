from os import read, write

from .tape import Tape


class Machine(object):
    def __init__(self, stdin, stdout):
        self.tape = Tape()
        self.stdin = stdin
        self.stdout = stdout

    def read(self):
        # buf = read(self.stdin, 1)[0]
        buf = self.stdin.read(1)[0]
        self.tape.set(ord(buf))

    def write(self):
        buf = chr(self.tape.get())
        # write(self.stdout, buf)
        self.stdout.write(buf)
