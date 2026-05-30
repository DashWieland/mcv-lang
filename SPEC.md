# The MCV Language Specification

Version 0.1.0

MCV is a stack-based, Turing-complete esoteric programming language. The source
code of an MCV program consists **only** of the characters `M`, `C`, and `V` —
no whitespace, no delimiters, no line breaks. A program is a single unbroken
string. The interpreter reads this stream left to right and decodes it into
instructions.

The architecture is adapted from [Whitespace](https://esolangs.org/wiki/Whitespace)
(Brady & Morris, 2003), which proved that three symbols suffice for a complete
language. Where Whitespace uses space/tab/linefeed, MCV uses M/C/V; the
instruction set, number encoding, and labels are MCV's own.

---

## 1. The decoding model

The lexer walks the source with a single cursor. The grammar is **prefix-free**:
at every decision point, the next one or two characters uniquely determine what
to read next, so no separators are needed. An instruction is decoded in three
stages:

```
[ IMP ][ opcode ][ optional parameter ]
```

* **IMP** (Instruction Modification Parameter) — selects a *category* of
  instruction.
* **opcode** — selects the specific instruction within that category.
* **parameter** — a number (for `PUSH`) or a label (for the five flow
  instructions that target one). All other instructions take no parameter.

If the stream ends in the middle of an instruction, or contains any character
other than `M`/`C`/`V`, decoding fails with a syntax error.

---

## 2. IMP layout

There are two single-character IMPs and one branching prefix. This is the same
structural trick Whitespace uses (two of its three symbols are standalone IMPs;
the third begins multi-character IMPs), chosen here so the most common
categories cost the fewest characters.

| IMP  | Category            |
|------|---------------------|
| `M`  | Stack manipulation  |
| `V`  | Flow control        |
| `CM` | Arithmetic          |
| `CC` | Heap access         |
| `CV` | I/O                 |

Because `M` and `V` are complete IMPs on their own, only `C` can begin a
two-character IMP — so the layout is unambiguous.

---

## 3. Instruction set

The **opcode** column is what follows the IMP. The **full** column is the
complete byte sequence (IMP + opcode) you would write in source.

### Stack manipulation — IMP `M`

| Instruction | opcode | full  | Effect                                             |
|-------------|--------|-------|----------------------------------------------------|
| `PUSH n`    | `M`    | `MM`+n| Push number *n* (encoded inline, see §4).          |
| `DUP`       | `CM`   | `MCM` | Duplicate the top of the stack.                    |
| `SWAP`      | `CC`   | `MCC` | Swap the top two stack items.                      |
| `DISCARD`   | `CV`   | `MCV` | Pop and discard the top of the stack.              |

> Note: `DISCARD` encodes as exactly `MCV` — the language discarding its own name.

### Arithmetic — IMP `CM`

Each pops `b` (top) then `a`, and pushes the result of `a OP b`.

| Instruction | opcode | full   | Effect            |
|-------------|--------|--------|-------------------|
| `ADD`       | `MM`   | `CMMM` | push `a + b`      |
| `SUB`       | `MC`   | `CMMC` | push `a - b`      |
| `MUL`       | `MV`   | `CMMV` | push `a * b`      |
| `DIV`       | `CM`   | `CMCM` | push `a // b`     |
| `MOD`       | `CC`   | `CMCC` | push `a % b`      |

`DIV` is floor division (rounds toward negative infinity) and `MOD` takes the
sign of the divisor — Python's `//` and `%` semantics. Dividing by zero is a
runtime error.

### Flow control — IMP `V`

| Instruction  | opcode | full       | Effect                                          |
|--------------|--------|------------|-------------------------------------------------|
| `MARK l`     | `MM`   | `VMM`+l    | Mark a label at this position (no runtime cost).|
| `CALL l`     | `MC`   | `VMC`+l    | Push return address, jump to label *l*.         |
| `JMP l`      | `MV`   | `VMV`+l    | Jump unconditionally to label *l*.              |
| `JZ l`       | `CM`   | `VCM`+l    | Pop; if it is `0`, jump to *l*.                 |
| `JNEG l`     | `CC`   | `VCC`+l    | Pop; if it is negative, jump to *l*.            |
| `RET`        | `CV`   | `VCV`      | Return to the address on top of the call stack. |
| `END`        | `VV`   | `VVV`      | Halt the program.                               |

### Heap access — IMP `CC`

| Instruction | opcode | full  | Effect                                                   |
|-------------|--------|-------|----------------------------------------------------------|
| `STORE`     | `M`    | `CCM` | Pop *value* then *address*; set `heap[address] = value`. |
| `RETRIEVE`  | `C`    | `CCC` | Pop *address*; push `heap[address]`.                     |

The heap is an integer-keyed store. Retrieving an address that was never stored
yields `0`.

### I/O — IMP `CV`

| Instruction | opcode | full   | Effect                                                       |
|-------------|--------|--------|--------------------------------------------------------------|
| `OUTCHAR`   | `MM`   | `CVMM` | Pop a number, write it as a Unicode character.               |
| `OUTNUM`    | `MC`   | `CVMC` | Pop a number, write its decimal representation.              |
| `READCHAR`  | `CM`   | `CVCM` | Pop *address*; read one character; store its code there.     |
| `READNUM`   | `CC`   | `CVCC` | Pop *address*; read a line, parse an integer; store it there.|

`READCHAR` stores `-1` at end of input (the EOF sentinel), so programs can
detect it (see `examples/cat.s`). `READNUM` raises a runtime error at EOF or on
unparseable input.

---

## 4. Number encoding

Numbers appear only as the parameter of `PUSH`. The encoding is:

```
[ sign ][ binary digits ][ V ]
```

* **sign** — `M` for non-negative, `C` for negative.
* **binary digits** — `M` = 0, `C` = 1, most-significant first.
* **terminator** — `V` ends the number.

An empty digit string (sign immediately followed by `V`) decodes to `0`. Both
`MV` (+0) and `CV` (−0) therefore mean `0`.

This is the "Option C" encoding from the design notes: two symbols carry binary
digits and the third terminates. A purely *ternary* scheme (M=0, C=1, V=2, using
all three symbols as digits) would be more thematically faithful to the
three-letter premise, but a ternary number leaves no spare single symbol for a
terminator and so needs a two-character delimiter. Binary-with-`V`-terminator is
simpler to parse and was chosen for v0.1; ternary remains a candidate for a
future revision.

Examples:

| n  | encoding |
|----|----------|
| 0  | `MMV`    |
| 1  | `MCV`    |
| 2  | `MCMV`   |
| 3  | `MCCV`   |
| 5  | `MCMCV`  |
| 10 | `MCMCMV` |
| −1 | `CCV`    |
| −5 | `CCMCV`  |

---

## 5. Labels

A label is **exactly three characters** drawn from `{M, C, V}`, giving 27
possible labels — enough for any reasonable MCV program. Labels follow the
opcode of `MARK`, `CALL`, `JMP`, `JZ`, and `JNEG`.

A label may be marked at most once; marking the same label twice is a runtime
error. Jumping to a label that was never marked is also a runtime error.

(The bundled assembler, `mcv.asm`, lets you write labels of 1–3 symbols and
left-pads them to width 3 with `M`, purely as a writing convenience.)

---

## 6. Execution model

* **Stack** — arbitrary-precision integers; the primary data structure.
* **Heap** — integer-keyed store of integers, for random access.
* **Call stack** — return addresses for `CALL` / `RET`.
* **Instruction pointer** — index into the decoded instruction list.

Before execution, a pre-pass scans all `MARK` instructions and records their
positions, so forward jumps work. The main loop then fetches the instruction at
the pointer, executes it, and advances — except for jumps, calls, and returns,
which set the pointer directly. `END`, or running past the last instruction,
halts the machine.

### Errors

* **Syntax errors** (`MCVSyntaxError`) — illegal character, truncated
  instruction, unknown opcode.
* **Runtime errors** (`MCVRuntimeError`) — stack underflow, division by zero,
  undefined or duplicate label, `RET` with an empty call stack, EOF while
  reading a number.

### Edge cases

* **Empty program** — decodes to zero instructions and halts immediately (no-op).
* **Non-halting program** — runs forever by design; there is no timeout.
* **Reading at EOF** — `READCHAR` yields `-1`; `READNUM` errors.

---

## 7. Worked example

Program: push 5, push 3, add, print the result as a number, halt.

Assembly:

```
push 5
push 3
add
outnum
end
```

Encoded MCV source (23 characters):

```
MMMCMCVMMMCCVCMMMCVMCVVV
```

Decoding it character by character:

| Segment   | IMP        | opcode      | meaning           |
|-----------|------------|-------------|-------------------|
| `MM MCMCV`| `M` stack  | `M` push    | `PUSH 5` (`MCMCV` = +`101`b = 5) |
| `MM MCCV` | `M` stack  | `M` push    | `PUSH 3` (`MCCV` = +`11`b = 3)   |
| `CM MM`   | `CM` arith | `MM` add    | `ADD` → push 8    |
| `CV MC`   | `CV` I/O   | `MC` outnum | print `8`         |
| `V VV`    | `V` flow   | `VV` end    | halt              |

Output:

```
8
```

To a librarian in the Library of Babel, the line `MMMCMCVMMMCCVCMMMCVMCVVV` is
just another wall of letters. It is also a program that prints `8`.
