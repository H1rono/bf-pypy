class Tape:
    def __init__(self) -> None:
        self._data = [0]
        self._ptr = 0

    def __str__(self) -> str:
        data_str = (f"@{v}" if i == self._ptr else f"{v}" for i, v in enumerate(self._data))
        data = ", ".join(data_str)
        return f"Tape[{data}]"

    def verify(self) -> bool:
        data_verify = (0 <= v < 256 for v in self._data)
        return len(self._data) > self._ptr and all(data_verify)

    @property
    def value(self) -> int:
        return self._data[self._ptr]

    @value.setter
    def value(self, value: int) -> None:
        self._data[self._ptr] = value

    def advance_by(self, diff: int) -> None:
        self._ptr += diff
        ext = self._ptr - len(self._data)
        if ext < 0:
            return None
        self._data += [0] * (ext + 1)

    def devance_by(self, diff: int) -> None:
        self._ptr -= diff
