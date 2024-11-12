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
MEMBERS = [INCREMENT, DECREMENT, ADVANCE, DEVANCE, WRITE, READ, LOOP_BEGIN, LOOP_END]


def is_token(token):
    """
    is_token(token: char) -> bool
    """
    return token in MEMBERS


class Token(object):
    def __init__(self, raw, position):
        """
        __init__(self, raw: str, position: (int, int))
        # position: (begin, end)
        """
        self.raw = raw
        begin, end = position
        self.pos_begin = begin
        self.pos_end = end

    def as_tuple(self):
        """
        as_tuple(self) -> (str, (int, int))
        """
        return (self.raw, (self.pos_begin, self.pos_end))


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
