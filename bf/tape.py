class Tape(object):
    def __init__(self):
        self.thetape = [0]
        self.position = 0

    def get(self):
        return self.thetape[self.position]

    def set(self, val):
        self.thetape[self.position] = val

    def inc_by(self, diff):
        self.thetape[self.position] += diff

    def dec_by(self, diff):
        self.thetape[self.position] -= diff

    def advance_by(self, pos_diff):
        self.position += pos_diff
        len_tape = len(self.thetape)
        if len_tape <= self.position:
            ext = [0] * (self.position - len_tape + 1)
            self.thetape.extend(ext)

    def devance_by(self, diff):
        self.position -= diff
