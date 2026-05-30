"""Lexer: decode a raw MCV string into a list of instructions.

An MCV program is an unbroken string of the characters M, C and V. The lexer
walks the string with a single cursor, reading one instruction at a time. The
grammar is *prefix-free*: at every branch the next character (or two) uniquely
determines what to read next, so no separators are needed.

See SPEC.md for the full grammar. Each decoded instruction is an ``Instr``:
a name plus an optional argument (an integer for PUSH, a 3-character label for
flow instructions that target one, otherwise ``None``).
"""

from __future__ import annotations

from typing import NamedTuple

from .errors import MCVSyntaxError

ALPHABET = frozenset("MCV")
LABEL_WIDTH = 3  # labels are exactly three symbols → 27 possible labels


class Instr(NamedTuple):
    name: str
    arg: object | None = None  # int (PUSH), str (label), or None


class _Cursor:
    """A read head over the MCV source, with helpful end-of-input errors."""

    def __init__(self, src: str):
        self.src = src
        self.i = 0

    def at_end(self) -> bool:
        return self.i >= len(self.src)

    def next(self, what: str) -> str:
        if self.at_end():
            raise MCVSyntaxError(f"program ended while reading {what}", self.i)
        ch = self.src[self.i]
        self.i += 1
        return ch


def _read_number(cur: _Cursor) -> int:
    """Sign (M=+, C=-) then binary digits (M=0, C=1), terminated by V.

    An empty digit string (sign immediately followed by V) decodes to 0, so
    +0 is ``MV`` and -0 is ``CV`` (both equal 0).
    """
    sign_ch = cur.next("a number sign")
    if sign_ch == "M":
        sign = 1
    elif sign_ch == "C":
        sign = -1
    else:  # 'V' would terminate before a sign was given
        raise MCVSyntaxError("number sign must be M (+) or C (-)", cur.i - 1)

    value = 0
    while True:
        ch = cur.next("number digits")
        if ch == "V":
            return sign * value
        if ch == "M":
            value = value * 2
        elif ch == "C":
            value = value * 2 + 1
        else:  # unreachable: only M/C/V exist, and V returned above
            raise MCVSyntaxError("invalid number digit", cur.i - 1)


def _read_label(cur: _Cursor) -> str:
    return "".join(cur.next("a label") for _ in range(LABEL_WIDTH))


def _read_stack(cur: _Cursor) -> Instr:
    op = cur.next("a stack opcode")
    if op == "M":
        return Instr("PUSH", _read_number(cur))
    if op == "C":
        sub = cur.next("a stack opcode")
        return {"M": Instr("DUP"), "C": Instr("SWAP"), "V": Instr("DISCARD")}.get(
            sub
        ) or _bad("stack", "C" + sub, cur)
    return _bad("stack", op, cur)


def _read_arith(cur: _Cursor) -> Instr:
    op = cur.next("an arithmetic opcode") + cur.next("an arithmetic opcode")
    name = {"MM": "ADD", "MC": "SUB", "MV": "MUL", "CM": "DIV", "CC": "MOD"}.get(op)
    return Instr(name) if name else _bad("arithmetic", op, cur)


def _read_heap(cur: _Cursor) -> Instr:
    op = cur.next("a heap opcode")
    name = {"M": "STORE", "C": "RETRIEVE"}.get(op)
    return Instr(name) if name else _bad("heap", op, cur)


def _read_io(cur: _Cursor) -> Instr:
    op = cur.next("an I/O opcode") + cur.next("an I/O opcode")
    name = {"MM": "OUTCHAR", "MC": "OUTNUM", "CM": "READCHAR", "CC": "READNUM"}.get(op)
    return Instr(name) if name else _bad("I/O", op, cur)


def _read_flow(cur: _Cursor) -> Instr:
    op = cur.next("a flow opcode") + cur.next("a flow opcode")
    if op in ("MM", "MC", "MV", "CM", "CC"):
        name = {"MM": "MARK", "MC": "CALL", "MV": "JMP", "CM": "JZ", "CC": "JNEG"}[op]
        return Instr(name, _read_label(cur))
    if op == "CV":
        return Instr("RET")
    if op == "VV":
        return Instr("END")
    return _bad("flow", op, cur)


def _bad(category: str, op: str, cur: _Cursor):
    raise MCVSyntaxError(f"unknown {category} opcode {op!r}", cur.i - len(op))


def lex(src: str) -> list[Instr]:
    """Decode an MCV source string into a list of instructions."""
    for i, ch in enumerate(src):
        if ch not in ALPHABET:
            raise MCVSyntaxError(f"illegal character {ch!r}; only M, C, V allowed", i)

    cur = _Cursor(src)
    program: list[Instr] = []
    while not cur.at_end():
        imp = cur.next("an IMP")
        if imp == "M":
            program.append(_read_stack(cur))
        elif imp == "V":
            program.append(_read_flow(cur))
        else:  # 'C' branches into arithmetic / heap / I/O
            kind = cur.next("an IMP")
            if kind == "M":
                program.append(_read_arith(cur))
            elif kind == "C":
                program.append(_read_heap(cur))
            elif kind == "V":
                program.append(_read_io(cur))
            else:  # unreachable given the alphabet check above
                _bad("IMP", "C" + kind, cur)
    return program
