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
    KIND_TOKEN = 0x86 # TO in telephone
    KIND_LOOP = 0x56 # LO in telephone

    def __init__(self, kind, token, loop):
        """
        __init__(self, kind: 'Self.Kind', token: Token | None, loop: list[Self] | None)
        kind == KIND_TOKEN => token is not None
        kind == KIND_LOOP => loop is not None
        """
        assert kind == Program.KIND_TOKEN or kind == Program.KIND_LOOP
        self.kind = kind
        # self._token: Token | None
        self.token = token
        # self._loop: list[Self] | None
        self.loop = loop
        if kind == Program.KIND_TOKEN:
            assert is_token(token) and loop is None
            return
        # kind == Program.KIND_LOOP
        assert isinstance(loop, list) and token is None
        _assert_all_program(loop)

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """
        to_str(self) -> str
        """
        if self.kind == Program.KIND_TOKEN:
            assert self.token is not None
            return "Program.token(%s)" % str(self.token)
        assert self.kind == Program.KIND_LOOP and self.loop is not None
        loop_len = len(self.loop)
        loop = ""
        for i, p in enumerate(self.loop):
            p_str = p.to_str()
            loop += "%s, " % p_str if i < loop_len - 1 else p_str
        return "Program.loop[%s]" % loop


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
