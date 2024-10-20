class Tape:
    def __init__(self):
        self._data = [0]
        self._ptr = 0

    def __str__(self):
        data_str = ("@%d" % v if i == self._ptr else str(v) for i, v in enumerate(self._data))
        data = ", ".join(data_str)
        return "Tape[%s]" % data

    def verify(self):
        """
        verify(self) -> bool
        """
        data_verify = (0 <= v < 256 for v in self._data)
        return len(self._data) > self._ptr and all(data_verify)

    @property
    def value(self):
        """
        value(self) -> int
        """
        return self._data[self._ptr]

    @value.setter
    def value(self, value):
        """
        value(self, value: int) -> None
        """
        assert isinstance(value, int)
        self._data[self._ptr] = value

    def advance_by(self, diff):
        """
        advance_by(self, diff: int) -> None
        """
        assert isinstance(diff, int)
        self._ptr += diff
        ext = self._ptr - len(self._data)
        if ext < 0:
            return None
        self._data += [0] * (ext + 1)

    def devance_by(self, diff):
        """
        devance_by(self, diff: int) -> None
        """
        assert isinstance(diff, int)
        self._ptr -= diff
