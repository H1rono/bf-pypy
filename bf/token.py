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
