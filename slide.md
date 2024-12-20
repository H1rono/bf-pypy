---
marp: true
---

# bf-pypy 最適化内容

commit: [`53754ee`](https://github.com/H1rono/bf-pypy/tree/53754ee427383636a770512c572ca34d685bfe82)

---

## 最適化2種類

- 連続するテープ操作
- ループ実行 → 掛け算への簡略化

---

## 連続するテープ操作

`+`, `-`, `>`, `<`で連続している部分はまとめられる

**例**: `>++ >+++ >+++ >+ <<<<-`

- 位置 `1` に `+2`
- 位置 `2` に `+3`
- (位置 `3`, `4` は略)
- 位置 `0` に `-1`
- ポインタの位置は動かない

---

## 連続するテープ操作: 例2

`>+ >+ >- >>+`

- `ポインタに対する相対位置` と `その位置での値の変化` の組:
    `(+1, +1)`, `(+2, +1)`, `(+3, -1)`, `(+5, +1)`
- `ポインタの移動量`: `+5`

---

## 連続するテープ操作: 一般化

`+`, `-`, `>`, `<`で連続している部分は以下の2情報で要約できる:

- `ポインタに対する相対位置` と `その位置での値の変化` の組 から成る列
    `val_diffs: list[tuple[int, int]]`
- `ポインタの移動量`
    `dpos: int`

実装: [`bf/parse.py:49`](https://github.com/H1rono/bf-pypy/blob/53754ee427383636a770512c572ca34d685bfe82/bf/parse.py#L49), [`bf/run.py:85`](https://github.com/H1rono/bf-pypy/blob/53754ee427383636a770512c572ca34d685bfe82/bf/run.py#L85)

---

## 掛け算への簡略化

ループ前後で、位置が変化しないものは簡略化できる

**例**: `[ - >>>+ <<< ]`

```text
ptr      0 ... +3  iteration
----------------------------
before  -1 ... +1    * n
after   -n ... +n    * 1
```

---

## 掛け算への簡略化: 例2

`[ >++ >+++ >+++ >+ <<<<- ]`

```text
ptr      0   +1   +2   +3   +4  iteration
-----------------------------------------
before  -1   +2   +3   +3   +1    * n
after   -n +2*n +3*n +3*n +1*n    * 1
```

位置 `0` での変化量が `-1` となっていることが重要!

---

## 掛け算への簡略化: 例外

`[ -<<<<+> [ <->-<<<<<<+>>>>>> ] < [ ->+< ] >>>> ]`

```text
ptr       0 -4 -3 -9
--------------------
outer    -n +n
inner@1     -m -m +m
inner@2     -l +l
```

**ループ同士が干渉している!**

---

## 掛け算への簡略化: 一般化

以下の条件を満たすループは簡略化可能

- 内部処理開始時のポインタ位置 と 終了時のポインタ位置 が変化しない
    → ループの「軸」が定まっている
- 内部処理にあるループ同士が「干渉」しない

実装: [`bf/parse.py:131`](https://github.com/H1rono/bf-pypy/blob/53754ee427383636a770512c572ca34d685bfe82/bf/parse.py#L131), [`bf/run.py:92`](https://github.com/H1rono/bf-pypy/blob/53754ee427383636a770512c572ca34d685bfe82/bf/run.py#L92)

---

## 変更結果

1文字のみの処理がI/Oのみに

```python
def instruction_one_char(program, instr, machine):
    _rng, _dpos, pc_rng = instr
    code = program_in(program, pc_rng)
    # assert code not in IO_OPS
    if code == WRITE:
        machine.write()
    elif code == READ:
        machine.read()
```

[`bf/run.py:58-65`](https://github.com/H1rono/bf-pypy/blob/53754ee427383636a770512c572ca34d685bfe82/bf/run.py#L58-L65)

---

## 計測結果

**`run-c`**

```text
real    0m21.412s
user    0m21.329s
sys     0m0.068s
```

**`example5-c`**

```text
real    0m3.588s
user    0m3.449s
sys     0m0.112s
```

---

## 敗因

- `val_diffs` をテープに適用する部分でループが発生
    → JITが最適化できなかった
- 内部データの表現にタプルを多用
    → タプル操作に時間を取られた?

ログの例↓

```text
+1164: p47 = getfield_gc_r(p36, descr=<FieldP tuple2.item0 8 pure>)
+1168: i48 = getfield_gc_i(p36, descr=<FieldS tuple2.item1 16 pure>)
+1172: i49 = getfield_gc_i(p47, descr=<FieldU tuple2.item1 16 pure>)
```

---

## 参考文献

- [ブラウザで動く高速 Brainfuck 実行環境を作った](https://zenn.dev/yukikurage/articles/e899c9bc14d73c)
