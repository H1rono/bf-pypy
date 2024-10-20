"""
```python
>>>> from bf import token
>>>> from bf.token import Token
>>>> token.from_char("+")
'+'
>>>> token.from_char(" ")
>>>> token.from_char("")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "bf/token.py", line 41, in from_char
    assert isinstance(c, str) and len(c) == 1
AssertionError
>>>> token.from_char("-")
'-'
>>>> ord("+")
43
>>>> token.from_byte(43)
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


class _TokenMeta(type):
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
    # __metaclass__ = _TokenMeta

    def __init__(self):
        return NotImplemented


def from_char(c):
    """
    from_char(c: str) -> Token | None
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



def from_byte(b):
    """
    from_byte(b: int) -> Token | None
    """
    # assert isinstance(b, int) and 0 <= b < 256
    return from_char(chr(b))
