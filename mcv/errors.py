"""Error types for the MCV interpreter."""


class MCVError(Exception):
    """Base class for all MCV errors."""


class MCVSyntaxError(MCVError):
    """Raised when the MCV source cannot be decoded into instructions.

    Examples: a character other than M/C/V, an instruction truncated before
    its parameters are complete, or an unknown opcode under some IMP.
    """

    def __init__(self, message: str, pos: int | None = None):
        self.pos = pos
        if pos is not None:
            message = f"{message} (at character {pos})"
        super().__init__(message)


class MCVRuntimeError(MCVError):
    """Raised while executing a program.

    Examples: stack underflow, division by zero, a jump to a label that was
    never marked, or a return with no matching call.
    """
