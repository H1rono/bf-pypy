from .tape import Tape


class Machine(object):
    def __init__(self, stdin, stdout):
        """
        __init__(self, stdin: File, stdout: File) -> None
        """
        assert hasattr(stdin, "read")
        assert hasattr(stdout, "write")
        self._tape = Tape()
        self._stdin = stdin
        self._stdout = stdout

    @property
    def tape(self):
        """
        tape(self) -> Tape
        """
        return self._tape

    def read(self):
        """
        read(self) -> None

        read 1byte from stdin, store to tape
        """
        b = self._stdin.read(1)
        if b is None:
            raise RuntimeError("Reached to EOF while reading stdin %s" % str(self._stdin))
        self._tape.value = b[0]

    def write(self):
        """
        write(self) -> None
        write 1byte from tape, to stdout
        """
        buf = bytearray([self._tape.value])
        self._stdout.write(buf)
