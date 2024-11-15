from rpython.rlib import types
from rpython.rlib.objectmodel import try_inline
from rpython.rlib.rarithmetic import r_uint


class Tape(object):
    __slots__ = ["thetape", "position"]

    def __init__(self):
        self.thetape = [0]
        self.position = 0

    def to_str(self):
        tape = ", ".join([
            ("@%d" if i == self.position else "%d") % v
            for i, v in enumerate(self.thetape)
        ])
        return "[%s]" % tape

    @try_inline
    def get(self):
        return self.thetape[self.position]

    @try_inline
    def set(self, val):
        self.thetape[self.position] = val

    @try_inline
    def inc_by(self, diff):
        self.thetape[self.position] += diff

    @try_inline
    def dec_by(self, diff):
        self.thetape[self.position] -= diff

    def advance_by(self, pos_diff):
        self.position += pos_diff
        len_tape = len(self.thetape)
        if len_tape <= self.position:
            ext = [0] * (self.position - len_tape + 1)
            self.thetape.extend(ext)

    @try_inline
    def devance_by(self, diff):
        self.position -= diff

    def accept_val_diffs(self, val_diffs):
        for dpos, dval in val_diffs:
            pos = self.position + dpos
            ext_len = pos - len(self.thetape)
            if ext_len >= 0:
                self.thetape.extend([0] * (ext_len + 1))
            self.thetape[pos] += dval

    @try_inline
    def accept_val_diffs_multiplied(self, val_diffs, mul_by):
        mul_val_diffs = [(dpos, dval * mul_by) for dpos, dval in val_diffs]
        self.accept_val_diffs(mul_val_diffs)

    @try_inline
    def mul_accept_val_diffs(self, val_diffs):
        self.accept_val_diffs_multiplied(val_diffs, self.get())
        # assert self.get() == 0


class DictTape(object):
    __slots__ = ["data", "position"]

    def __init__(self):
        self.data = {}
        self.position = 0

    def get(self):
        return self.data.get(self.position, 0)

    def set(self, val):
        assert isinstance(val, int)
        self.data[self.position] = val

    def inc_by(self, diff):
        assert isinstance(diff, int)
        self.set(self.get() + diff)

    def dec_by(self, diff):
        assert isinstance(diff, int)
        self.set(self.get() - diff)

    def advance_by(self, pos_diff):
        assert isinstance(pos_diff, int)
        self.position += pos_diff

    def devance_by(self, pos_diff):
        assert isinstance(pos_diff, int)
        self.position -= pos_diff

    def accept_val_diffs(self, val_diffs):
        for dpos, dval in val_diffs:
            pos = self.position + dpos
            self.data[pos] = self.data.get(pos, 0) + dval

    def mul_accept_val_diffs(self, val_diffs):
        mul_by = self.get()
        mul_val_diffs = [(dpos, dval * mul_by) for dpos, dval in val_diffs]
        self.accept_val_diffs(mul_val_diffs)
        # assert self.get() == 0

    def collect_val_diffs(self):
        return [(dp, dv) for dp, dv in self.data.items()]


s_tape = types.instance(Tape)
s_dict_tape = types.instance(DictTape)
