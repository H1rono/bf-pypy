from enum import Enum


class Token(Enum):
    INCREMENT = "+"
    DECREMENT = "-"
    ADVANCE = ">"
    DEVANCE = "<"
    WRITE = "."
    READ = ","
    LOOP_BEGIN = "["
    LOOP_END = "]"

    @classmethod
    def from_char(cls, c):
        """
        from_char(cls, c: str) -> Self | None
        """
        assert isinstance(c, str) and len(c) == 1
        return {
            "+": cls.INCREMENT,
            "-": cls.DECREMENT,
            ">": cls.ADVANCE,
            "<": cls.DEVANCE,
            ".": cls.WRITE,
            ",": cls.READ,
            "[": cls.LOOP_BEGIN,
            "]": cls.LOOP_END,
        }.get(c, None)

    @classmethod
    def from_byte(cls, b):
        """
        from_byte(cls, b: int) -> Self | None
        """
        assert isinstance(b, int) and 0 <= b < 256
        return cls.from_char(chr(b))
