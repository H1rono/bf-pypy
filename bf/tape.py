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

    def accept_val_diffs(self, val_diffs):
        for dpos, dval in val_diffs:
            pos = self.position + dpos
            ext_len = pos - len(self.thetape)
            if ext_len >= 0:
                self.thetape.extend([0] * (ext_len + 1))
            self.thetape[pos] += dval

    def mul_accept_val_diffs(self, val_diffs):
        mul_by = self.get()
        mul_val_diffs = [(dpos, dval * mul_by) for dpos, dval in val_diffs]
        self.accept_val_diffs(mul_val_diffs)
        self.set(0)
