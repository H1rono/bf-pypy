from io import RawIOBase

from .tape import Tape


class Machine:
    def __init__(self, stdin: RawIOBase, stdout: RawIOBase) -> None:
        assert stdin.readable()
        assert stdout.writable()
        self._tape = Tape()
        self._stdin = stdin
        self._stdout = stdout

    @property
    def tape(self) -> Tape:
        return self._tape

    def read(self) -> None:
        b = self._stdin.read(1)
        if b is None:
            raise RuntimeError(f"Reached to EOF while reading stdin {self._stdin}")
        self._tape.value = b[0]

    def write(self) -> None:
        buf = bytes([self._tape.value])
        self._stdout.write(buf)
