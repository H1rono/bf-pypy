from os import read, write

from rpython.rlib import jit
from rpython.rlib.types import instance
from rpython.rlib.objectmodel import try_inline

from .tape import Tape


class Machine(object):
    __slots__ = ["tape", "stdin", "stdout"]

    def __init__(self, stdin, stdout):
        self.tape = jit.hint(Tape(), access_directory=True)
        self.stdin = jit.hint(stdin, access_directory=True)
        self.stdout = jit.hint(stdout, access_directory=True)

    @try_inline
    def read(self):
        # buf = read(self.stdin, 1)[0]
        buf = self.stdin.read(1)[0]
        self.tape.set(ord(buf))

    @try_inline
    def write(self):
        buf = chr(self.tape.get())
        # write(self.stdout, buf)
        self.stdout.write(buf)


s_machine = instance(Machine)
