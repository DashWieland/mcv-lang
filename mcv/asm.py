"""A tiny assembler: human-readable mnemonics -> MCV source.

This is a development convenience, not part of the language. Writing M/C/V by
hand is error-prone, so the example programs are authored in this mnemonic form
and assembled down to strict MCV. The mnemonics map one-to-one onto the
instruction set in SPEC.md.

Assembly syntax (one instruction per line, '#' starts a comment):

    push 72        # an integer literal
    dup
    add
    mark LOL       # a label is 1-3 letters drawn from M/C/V
    jmp  LOL
    outchar

Run ``python -m mcv.asm file.s`` to print the assembled MCV string.
"""

from __future__ import annotations

import sys

from .lexer import LABEL_WIDTH

# mnemonic -> the MCV opcode bytes (IMP + opcode), excluding any parameter.
_OPCODES = {
    # stack
    "push": "MM",  # followed by an encoded number
    "dup": "MCM",
    "swap": "MCC",
    "discard": "MCV",
    # arithmetic
    "add": "CMMM",
    "sub": "CMMC",
    "mul": "CMMV",
    "div": "CMCM",
    "mod": "CMCC",
    # flow control
    "mark": "VMM",  # followed by a label
    "call": "VMC",  # followed by a label
    "jmp": "VMV",  # followed by a label
    "jz": "VCM",  # followed by a label
    "jneg": "VCC",  # followed by a label
    "ret": "VCV",
    "end": "VVV",
    # heap
    "store": "CCM",
    "retrieve": "CCC",
    # I/O
    "outchar": "CVMM",
    "outnum": "CVMC",
    "readchar": "CVCM",
    "readnum": "CVCC",
}

_TAKES_NUMBER = {"push"}
_TAKES_LABEL = {"mark", "call", "jmp", "jz", "jneg"}


def encode_number(n: int) -> str:
    """Encode an integer as MCV: sign (M=+, C=-), binary digits, V terminator."""
    sign = "M" if n >= 0 else "C"
    digits = "".join("C" if bit == "1" else "M" for bit in format(abs(n), "b"))
    # format(0, "b") == "0" -> a single M digit; that is fine and decodes to 0.
    return sign + digits + "V"


def encode_label(label: str) -> str:
    if not (1 <= len(label) <= LABEL_WIDTH) or any(c not in "MCV" for c in label):
        raise ValueError(f"label {label!r} must be 1-{LABEL_WIDTH} chars from M/C/V")
    return label.rjust(LABEL_WIDTH, "M")  # pad to fixed width with M


def assemble(text: str) -> str:
    out: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        mnem, args = parts[0].lower(), parts[1:]
        if mnem not in _OPCODES:
            raise ValueError(f"line {lineno}: unknown mnemonic {mnem!r}")
        out.append(_OPCODES[mnem])
        if mnem in _TAKES_NUMBER:
            out.append(encode_number(int(args[0])))
        elif mnem in _TAKES_LABEL:
            out.append(encode_label(args[0]))
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python -m mcv.asm FILE.s", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        print(assemble(f.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
