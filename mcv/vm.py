"""The MCV virtual machine: a stack of arbitrary-precision integers, a heap
(key-value store), a call stack, and an instruction pointer.

The VM takes a list of decoded ``Instr`` (from the lexer) and runs it. I/O
streams are injectable so the machine can be driven in tests without touching
the real stdin/stdout.
"""

from __future__ import annotations

import sys
from typing import TextIO

from .errors import MCVRuntimeError
from .lexer import Instr


class VM:
    def __init__(
        self,
        program: list[Instr],
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
        trace: bool = False,
    ):
        self.program = program
        self.stdin = stdin if stdin is not None else sys.stdin
        self.stdout = stdout if stdout is not None else sys.stdout
        self.trace = trace

        self.stack: list[int] = []
        self.heap: dict[int, int] = {}
        self.call_stack: list[int] = []
        self.labels = self._scan_labels(program)
        self.ip = 0

    @staticmethod
    def _scan_labels(program: list[Instr]) -> dict[str, int]:
        """Pre-pass: map each MARK label to its instruction index.

        A label may only be marked once; a duplicate is a runtime error so the
        target of a jump is never ambiguous.
        """
        labels: dict[str, int] = {}
        for idx, instr in enumerate(program):
            if instr.name == "MARK":
                if instr.arg in labels:
                    raise MCVRuntimeError(f"label {instr.arg!r} marked more than once")
                labels[instr.arg] = idx
        return labels

    # --- stack helpers -----------------------------------------------------

    def _pop(self) -> int:
        if not self.stack:
            raise MCVRuntimeError("stack underflow")
        return self.stack.pop()

    def _label(self, name: str) -> int:
        if name not in self.labels:
            raise MCVRuntimeError(f"jump to undefined label {name!r}")
        return self.labels[name]

    # --- main loop ---------------------------------------------------------

    def run(self) -> None:
        while self.ip < len(self.program):
            instr = self.program[self.ip]
            if self.trace:
                self._emit_trace(instr)
            # execute() returns the next ip, or None to advance by one.
            nxt = self._execute(instr)
            self.ip = self.ip + 1 if nxt is None else nxt

    def _emit_trace(self, instr: Instr) -> None:
        arg = "" if instr.arg is None else f" {instr.arg}"
        print(
            f"[{self.ip:4}] {instr.name}{arg:<8} stack={self.stack}",
            file=sys.stderr,
        )

    def _execute(self, instr: Instr) -> int | None:
        name = instr.name

        # --- stack manipulation ---
        if name == "PUSH":
            self.stack.append(instr.arg)
        elif name == "DUP":
            self.stack.append(self._peek())
        elif name == "SWAP":
            a, b = self._pop(), self._pop()
            self.stack.append(a)
            self.stack.append(b)
        elif name == "DISCARD":
            self._pop()

        # --- arithmetic (pop b, pop a, push a OP b) ---
        elif name in ("ADD", "SUB", "MUL", "DIV", "MOD"):
            b, a = self._pop(), self._pop()
            self.stack.append(self._arith(name, a, b))

        # --- flow control ---
        elif name == "MARK":
            pass  # resolved in the pre-pass; nothing to do at runtime
        elif name == "JMP":
            return self._label(instr.arg)
        elif name == "JZ":
            if self._pop() == 0:
                return self._label(instr.arg)
        elif name == "JNEG":
            if self._pop() < 0:
                return self._label(instr.arg)
        elif name == "CALL":
            self.call_stack.append(self.ip + 1)
            return self._label(instr.arg)
        elif name == "RET":
            if not self.call_stack:
                raise MCVRuntimeError("return with no matching call")
            return self.call_stack.pop()
        elif name == "END":
            return len(self.program)  # jump past the end → loop exits

        # --- heap access ---
        elif name == "STORE":
            value, addr = self._pop(), self._pop()
            self.heap[addr] = value
        elif name == "RETRIEVE":
            addr = self._pop()
            self.stack.append(self.heap.get(addr, 0))  # unset address reads as 0

        # --- I/O ---
        elif name == "OUTCHAR":
            self.stdout.write(chr(self._pop()))
            self.stdout.flush()
        elif name == "OUTNUM":
            self.stdout.write(str(self._pop()))
            self.stdout.flush()
        elif name == "READCHAR":
            self.heap[self._pop()] = self._read_char()
        elif name == "READNUM":
            self.heap[self._pop()] = self._read_num()

        else:  # unreachable: the lexer only emits known names
            raise MCVRuntimeError(f"unknown instruction {name!r}")

        return None

    def _peek(self) -> int:
        if not self.stack:
            raise MCVRuntimeError("stack underflow")
        return self.stack[-1]

    @staticmethod
    def _arith(name: str, a: int, b: int) -> int:
        if name == "ADD":
            return a + b
        if name == "SUB":
            return a - b
        if name == "MUL":
            return a * b
        if b == 0:
            raise MCVRuntimeError(f"{name.lower()} by zero")
        if name == "DIV":
            return a // b  # floor division (rounds toward negative infinity)
        return a % b  # MOD, sign follows the divisor (Python semantics)

    def _read_char(self) -> int:
        ch = self.stdin.read(1)
        if ch == "":
            return -1  # EOF sentinel, so programs (e.g. cat) can detect it
        return ord(ch)

    def _read_num(self) -> int:
        line = self.stdin.readline()
        if line == "":
            raise MCVRuntimeError("end of input while reading a number")
        try:
            return int(line.strip())
        except ValueError:
            raise MCVRuntimeError(f"expected a number, got {line.strip()!r}")
