"""
```python
>>>> from bf.tape import Tape
>>>> t = Tape()
>>>> print(t)
Tape[@0]
>>>> t.value += 10
>>>> print(t)
Tape[@10]
>>>> t.value
10
>>>> t.advance_by(3)
>>>> t.value
0
>>>> t.verify()
True
>>>> t.value -= 5
>>>> t.verify()
False
>>>> print(t)
Tape[10, 0, 0, @-5]
```
"""

from rpython.rlib.objectmodel import try_inline


class Tape(object):
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

    def value(self):
        """
        value(self) -> int
        """
        return self._data[self._ptr]

    def set_value(self, value):
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
            return
        self._data += [0] * (ext + 1)

    def devance_by(self, diff):
        """
        devance_by(self, diff: int) -> None
        """
        assert isinstance(diff, int)
        self._ptr -= diff
