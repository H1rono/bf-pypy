from enum import Enum

from typing_extensions import Self


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
    def from_char(cls, c: str) -> Self | None:
        assert len(c) == 1
        match c:
            case "+":
                return cls.INCREMENT  # type: ignore
            case "-":
                return cls.DECREMENT  # type: ignore
            case ">":
                return cls.ADVANCE  # type: ignore
            case "<":
                return cls.DEVANCE  # type: ignore
            case ".":
                return cls.WRITE  # type: ignore
            case ",":
                return cls.READ  # type: ignore
            case "[":
                return cls.LOOP_BEGIN  # type: ignore
            case "]":
                return cls.LOOP_END  # type: ignore
            case _:
                return None

    @classmethod
    def from_byte(cls, b: int) -> Self | None:
        assert 0 <= b < 256
        return cls.from_char(chr(b))
