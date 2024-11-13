from os import read


INCREMENT = "+"
DECREMENT = "-"
ADVANCE = ">"
DEVANCE = "<"
LOOP_BEGIN = "["
LOOP_END = "]"
READ = ","
WRITE = "."
MEMBERS = [INCREMENT, DECREMENT, ADVANCE, DEVANCE, LOOP_BEGIN, LOOP_END, READ, WRITE]
SIMPLES = [INCREMENT, DECREMENT, ADVANCE, DEVANCE]


class Tokens(object):
    def __init__(self, file):
        self.file = file.fileno()

    def __iter__(self):
        return self

    def next(self):
        t = None
        while t is None:
            c = read(self.file, 1)
            if not c:
                raise StopIteration()
            if c in MEMBERS:
                t = c
        return t

    def enumerate(self):
        return Enumerate(self)


class Enumerate(object):
    def __init__(self, tokens):
        assert isinstance(tokens, Tokens)
        self._tokens = tokens
        self._i = 0

    def __iter__(self):
        return self

    def next(self):
        t = self._tokens.next()
        i = self._i
        self._i += 1
        return (i, t)
