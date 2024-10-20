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
        assert isinstance(value, list) and all(isinstance(v, Program) for v in value)
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

    @classmethod
    def token(cls, value):
        """
        token(cls, value: Token) -> Self
        """
        assert isinstance(value, Token)
        return cls(cls.KIND_TOKEN, value)

    @classmethod
    def loop(cls, value):
        """
        token(cls, value: Iterator<Item=Program>) -> Self
        """
        value = list(value)
        assert all(isinstance(v, cls) for v in value)
        return cls(cls.KIND_LOOP, value)
