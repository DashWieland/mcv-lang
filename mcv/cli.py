"""Command-line interface for the MCV interpreter.

Usage:
    mcv run program.mcv            # run a .mcv file
    mcv run --raw "MMMCMCV..."     # run a literal MCV string
    echo "MM..." | mcv run --stdin # run MCV read from stdin
    mcv run --trace program.mcv    # print each instruction as it executes

Any character in the source that is not M, C or V is a syntax error. (When
reading a file we strip surrounding whitespace/newlines first, so a trailing
newline in an editor does not break an otherwise-valid program.)
"""

from __future__ import annotations

import argparse
import sys

from .errors import MCVError
from .lexer import lex
from .vm import VM


def _load_source(args: argparse.Namespace) -> str:
    if args.raw is not None:
        return args.raw
    if args.stdin:
        return sys.stdin.read()
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    raise SystemExit("error: provide a FILE, --raw STRING, or --stdin")


def _clean(source: str) -> str:
    """Drop surrounding whitespace; M/C/V-only is enforced by the lexer."""
    return source.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcv", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="run an MCV program")
    src = run_p.add_mutually_exclusive_group()
    src.add_argument("file", nargs="?", help="path to a .mcv file")
    src.add_argument("--raw", metavar="MCV", help="MCV source as a literal string")
    src.add_argument(
        "--stdin", action="store_true", help="read MCV source from standard input"
    )
    run_p.add_argument(
        "--trace",
        action="store_true",
        help="print each instruction and the stack to stderr as it runs",
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        if args.stdin and args.trace:
            # Reading the program from stdin and the program reading runtime
            # input from stdin can't both work; warn but proceed.
            pass
        source = _clean(_load_source(args))
        try:
            vm = VM(lex(source), trace=args.trace)
            vm.run()
        except MCVError as exc:
            print(f"mcv: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        except BrokenPipeError:
            # Downstream closed the pipe (e.g. `mcv run loop.mcv | head`).
            # That is normal; exit quietly instead of dumping a traceback.
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
