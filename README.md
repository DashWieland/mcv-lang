# MCV

> One which my father saw in a hexagon on circuit fifteen ninety-four was made
> up of the letters MCV, perversely repeated from the first line to the last.
>
> I cannot combine some characters *dhcmrlchtdj* which the divine Library has
> not foreseen and which in one of its secret tongues do not contain a terrible
> meaning. No one can articulate a syllable which is not filled with tenderness
> and fear, which is not, in one of these languages, the powerful name of a god.
>
> — Jorge Luis Borges, *The Library of Babel* (1941); trans. James E. Irby,
> *Labyrinths* (1962)

The narrator concludes that "four hundred and ten pages of inalterable MCV's
cannot correspond to any language, no matter how dialectical or rudimentary it
may be."

The narrator is wrong.

## What is MCV?

MCV is a stack-based, Turing-complete programming language whose source code
contains only the letters **M**, **C**, and **V**. No spaces, no punctuation, no
line breaks — just an unbroken wall of three letters, exactly like the book
Borges describes. The interpreter reads the wall and decodes it into
instructions.

It is an esoteric language in the tradition of
[Whitespace](https://esolangs.org/wiki/Whitespace), whose three-symbol
architecture proves the thing can be done at all. MCV borrows that skeleton and
gives it its own instruction set, number encoding, and labels. See
[`SPEC.md`](SPEC.md) for the formal grammar.

## A quick example

Here is a complete MCV program:

```
MMMCMCVMMMCCVCMMMCVMCVVV
```

It pushes 5, pushes 3, adds them, prints the result, and halts. It outputs:

```
8
```

The same program with the seams shown:

| `MM`+`MCMCV` | `MM`+`MCCV` | `CMMM` | `CVMC` | `VVV` |
|--------------|-------------|--------|--------|-------|
| push 5       | push 3      | add    | print  | halt  |

That is the whole joke, really: the contrast between the seemingly meaningless
string of letters and the perfectly ordinary arithmetic it performs.

## A note on provenance

Every valid MCV program is, by definition, a string of M's, C's, and V's — which
means every valid MCV program already exists, in full, on some shelf in the
Library of Babel. We did not *write* the program above so much as *locate* it.
You can confirm this yourself: paste the source into the search box at
[libraryofbabel.info](https://libraryofbabel.info) and it will hand you the
hexagon, wall, shelf, volume, and page where the book has sat, untouched, since
before the language existed.

The narrator's father found 410 pages of inalterable MCV's and saw nothing in
them. He was holding a library of programs and could not run a single one.

## Installation

```bash
pip install mcv-lang
```

Or from a clone:

```bash
git clone https://github.com/dashw/mcv && cd mcv
pip install -e .
```

No dependencies. Requires Python 3.10+.

## Usage

```bash
mcv run program.mcv               # run a .mcv file
mcv run --raw "MMMCMCVMMMCCVCMMMCVMCVVV"   # run a literal string
echo "MMMCMCVMMM..." | mcv run --stdin     # run MCV from stdin
mcv run --trace program.mcv       # print each instruction as it executes
```

(`python -m mcv run ...` works too, if you have not installed the script.)

As a library:

```python
import mcv
mcv.run("MMMCMCVMMMCCVCMMMCVMCVVV")   # prints: 8
```

## Examples

The [`examples/`](examples/) directory contains annotated programs:

| Program             | What it does                                            |
|---------------------|---------------------------------------------------------|
| `hello.mcv`         | Prints `Hello, World!`                                  |
| `fibonacci.mcv`     | Prints the first 10 Fibonacci numbers                   |
| `cat.mcv`           | Echoes input to output until EOF                        |
| `truth_machine.mcv` | Reads N; prints 0 and halts, or prints 1 forever        |

Each is written in a small mnemonic assembly (`.s`) and compiled to strict MCV.
See [`examples/README.md`](examples/README.md) for traces.

## Writing MCV

Writing M/C/V by hand is, as Borges warns, full of tenderness and fear. A tiny
assembler ships with the package for sanity's sake:

```bash
python -m mcv.asm examples/hello.s > hello.mcv
```

It is a convenience, not part of the language. The language is the wall of
letters.

## Language reference

The complete specification — IMP layout, every opcode, number encoding, labels,
and the execution model — is in [`SPEC.md`](SPEC.md).

## Acknowledgments

- **Jorge Luis Borges**, for *The Library of Babel*, and for a narrator so sure
  that 410 pages of MCV could mean nothing.
- **Edwin Brady and Chris Morris**, for Whitespace, which showed that three
  symbols are enough.
- **Jonathan Basile**, whose [libraryofbabel.info](https://libraryofbabel.info)
  makes the provenance gag literally true.
- The **esolang community**, for taking jokes exactly this seriously.

## License

MIT. See [`LICENSE`](LICENSE).
