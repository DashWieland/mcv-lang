"""MCV: an esoteric programming language whose source is only M, C and V.

A wall of MCV's, as found by the narrator's father in Borges's "The Library of
Babel," decoded into a Turing-complete stack machine.
"""

from .errors import MCVError, MCVRuntimeError, MCVSyntaxError
from .lexer import Instr, lex
from .vm import VM

__version__ = "0.1.0"

__all__ = [
    "Instr",
    "MCVError",
    "MCVRuntimeError",
    "MCVSyntaxError",
    "VM",
    "lex",
    "run",
]


def run(source: str, **kwargs) -> VM:
    """Lex and execute an MCV source string. Returns the halted VM."""
    vm = VM(lex(source), **kwargs)
    vm.run()
    return vm
