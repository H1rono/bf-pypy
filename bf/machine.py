from os import write

from .tape import Tape


class Machine(object):
    def __init__(self, stdin, stdout):
        """
        __init__(self, stdin: File, stdout: File) -> None
        """
        # TODO: add some assertion
        # assert hasattr(stdin, "read")
        # assert hasattr(stdout, "write")
        self.tape = Tape()
        self._stdin = stdin
        self._stdin_line = ""
        self._stdout = stdout.fileno()

    def read(self):
        """
        read(self) -> None

        read 1byte from stdin, store to tape
        """
        if len(self._stdin_line) == 0:
            self._stdin_line = self._stdin.readline(100)
        if len(self._stdin_line) == 0:
            raise RuntimeError("Reached to EOF while reading stdin %s" % str(self._stdin))
        head = self._stdin_line[0]
        tail = self._stdin_line[1:]
        self._stdin_line = tail
        self.tape.set_value(ord(head))

    def write(self):
        """
        write(self) -> None
        write 1byte from tape, to stdout
        """
        buf = chr(self.tape.value())
        # self._stdout.write(buf)
        write(self._stdout, str(buf))
