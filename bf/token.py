"""
```python
>>>> from bf import token
>>>> from bf.token import Token
>>>> Token.from_char("+")
'+'
>>>> Token.from_char(" ")
>>>> Token.from_char("")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "bf/token.py", line 41, in from_char
    assert isinstance(c, str) and len(c) == 1
AssertionError
>>>> Token.from_char("-")
'-'
>>>> ord("+")
43
>>>> Token.from_byte(43)
'+'
```
"""


INCREMENT = "+"
DECREMENT = "-"
ADVANCE = ">"
DEVANCE = "<"
WRITE = "."
READ = ","
LOOP_BEGIN = "["
LOOP_END = "]"


class TokenMeta(type):
    def __instancecheck__(self, other):
        """
        __instancecheck(self, other: type) -> bool
        """
        return other in self.members()

    def members(self):
        """
        members(self) -> list[Token]
        """
        return [
            INCREMENT, DECREMENT,
            ADVANCE, DEVANCE,
            WRITE, READ,
            LOOP_BEGIN, LOOP_END
        ]


class Token(object):
    __metaclass__ = TokenMeta

    def __init__(self):
        return NotImplemented

    @classmethod
    def from_char(cls, c):
        """
        from_char(cls, c: str) -> Self | None
        """
        assert isinstance(c, str) and len(c) == 1
        return {
            "+": INCREMENT,
            "-": DECREMENT,
            ">": ADVANCE,
            "<": DEVANCE,
            ".": WRITE,
            ",": READ,
            "[": LOOP_BEGIN,
            "]": LOOP_END,
        }.get(c, None)

    @classmethod
    def from_byte(cls, b):
        """
        from_byte(cls, b: int) -> Self | None
        """
        assert isinstance(b, int) and 0 <= b < 256
        return cls.from_char(chr(b))
