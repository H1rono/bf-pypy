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

from .token import Token, is_token


class Program(object):
    KIND_TOKEN = "PROGRAM_TOKEN"
    KIND_LOOP = "PROGRAM_LOOP"

    def __init__(self, kind, token, loop):
        """
        __init__(self, kind: 'Self.Kind', token: Token | None, loop: list[Self] | None)
        """
        assert kind == Program.KIND_TOKEN or kind == Program.KIND_LOOP
        self._kind = kind
        # self._token: Token | None
        self._token = token
        # self._loop: list[Self] | None
        self._loop = loop
        if kind == Program.KIND_TOKEN:
            assert is_token(token) and loop is None
            return
        # kind == Program.KIND_LOOP
        assert isinstance(loop, list) and token is None
        _assert_all_program(loop)
        self._loop = loop

    def __str__(self):
        if self._kind == Program.KIND_TOKEN:
            assert self._token is not None
            return "Program.token(%s)" % str(self._token)
        assert self._loop is not None
        loop = ", ".join(str(p) for p in self._loop)
        return "Program.loop[%s]" % loop

    @property
    def kind(self):
        """
        kind(self) -> 'Self.Kind'
        """
        return self._kind

    @property
    def token(self):
        """
        token(self) -> Token | None
        """
        return self._token

    @property
    def loop(self):
        """
        loop(self) -> list[Self] | None
        """
        return self._loop


def _assert_all_program(it):
    """
    _assert_all_program(it: Iterator<Item=(Maybe) Program>)
    """
    for v in it:
        assert isinstance(v, Program)


def token(value):
    """
    token(value: Token) -> Program
    """
    assert is_token(value)
    return Program(Program.KIND_TOKEN, value, None)


def loop(value):
    """
    loop(value: Iterator<Item=Program>) -> Program
    """
    value = [v for v in value]
    _assert_all_program(value)
    return Program(Program.KIND_LOOP, None, value)
