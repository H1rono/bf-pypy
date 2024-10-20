"""
```python
>>>> # Program = Program.token(Token) | Program.loop(list[Program])
>>>> from bf.program import Program
>>>> p = Program.token("+")
>>>> print p
Program.token(+)
>>>> p_loop = Program.loop([p])
>>>> print p_loop
Program.loop[Program.token(+)]
```
"""

from .token import Token


class Program(object):
    KIND_TOKEN = "PROGRAM_TOKEN"
    KIND_LOOP = "PROGRAM_LOOP"

    def __init__(self, kind, value):
        """
        __init__(self, kind: 'Self.Kind', value: Token | list[Self])
        """
        assert kind == Program.KIND_TOKEN or kind == Program.KIND_LOOP
        self._kind = kind
        if kind == Program.KIND_TOKEN:
            assert isinstance(value, Token)
            self._value = value
            return
        # kind == Program.KIND_LOOP
        assert isinstance(value, list)
        _assert_all_program(value)
        self._value = value

    def __str__(self):
        if self._kind == Program.KIND_TOKEN:
            return "Program.token(%s)" % str(self._value)
        loop = ", ".join(str(p) for p in self._value)
        return "Program.loop[%s]" % loop

    @property
    def kind(self):
        """
        kind(self) -> 'Self.Kind'
        """
        return self._kind

    @property
    def value(self):
        """
        value(self) -> Token | list[Self]
        """
        return self._value


def _assert_all_program(it):
    """
    _assert_all_program(it: Iterator<Item=(Maybe) Program>)
    """
    for v in it:
        assert isinstance(v, Program)


def new_token(value):
    """
    new_token(value: Token) -> Program
    """
    assert isinstance(value, Token)
    return Program(Program.KIND_TOKEN, value)


def new_loop(value):
    """
    new_loop(value: Iterator<Item=Program>) -> Program
    """
    value = [v for v in value]
    _assert_all_program(value)
    return Program(Program.KIND_LOOP, value)
