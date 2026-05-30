# MCV Examples

Each program here exists twice:

* a `.s` file — human-readable mnemonic assembly, with comments;
* a `.mcv` file — the strict MCV source, compiled from the `.s` with the bundled
  assembler.

Regenerate a `.mcv` from its source with:

```bash
python -m mcv.asm hello.s > hello.mcv
```

Run any program with:

```bash
mcv run hello.mcv
# or, before installing:
python -m mcv run hello.mcv
```

Add `--trace` to watch each instruction and the stack as it executes.

---

## hello.mcv

Prints `Hello, World!` followed by a newline. The simplest possible structure:
for each character, push its ASCII code and `outchar` it.

```
$ mcv run hello.mcv
Hello, World!
```

## fibonacci.mcv

Prints the first 10 Fibonacci numbers, one per line. Uses the heap as three
registers — `a`, `b`, and a countdown — and loops with a conditional jump.

```
$ mcv run fibonacci.mcv
0
1
1
2
3
5
8
13
21
34
```

Decoded shape: initialize `heap[0]=0`, `heap[1]=1`, `heap[2]=10`; loop while the
counter is nonzero, printing `a`, then advance `(a, b) <- (b, a+b)` and decrement
the counter.

## cat.mcv

Echoes standard input to standard output, one character at a time, until EOF.
`readchar` stores `-1` at end of input; the program duplicates each character,
tests the copy with `jneg`, and stops when it goes negative.

```
$ echo "the Library is total" | mcv run cat.mcv
the Library is total
```

Decoded shape:

```
loop: readchar into heap[0]
      retrieve, dup
      jneg done        # EOF (-1) is the only negative value
      outchar
      jmp loop
done: discard; end
```

## truth_machine.mcv

The canonical esolang sanity check. Reads a number N:

* if `N == 0`, prints `0` once and halts;
* otherwise, prints `1` forever.

```
$ echo 0 | mcv run truth_machine.mcv
0
$ echo 1 | mcv run truth_machine.mcv
1111111111...    # until you stop it (Ctrl-C)
```

## A note on the quine

A self-reproducing MCV program (`quine.mcv`) is a genuine stretch goal — hard in
any language that cannot read its own source, and harder when the only literals
you have are M, C, and V. It is left as an exercise, and as bait. The book is
out there; someone only has to find it.
