import io

import pytest

from mcv import lex
from mcv.asm import assemble
from mcv.errors import MCVRuntimeError
from mcv.vm import VM


def run(asm_text, stdin=""):
    out = io.StringIO()
    vm = VM(lex(assemble(asm_text)), stdin=io.StringIO(stdin), stdout=out)
    vm.run()
    return vm, out.getvalue()


def test_push_and_arithmetic():
    vm, _ = run("push 20\npush 6\nsub")  # 20 - 6
    assert vm.stack == [14]


@pytest.mark.parametrize(
    "op,expected",
    [("add", 13), ("sub", 7), ("mul", 30), ("div", 3), ("mod", 1)],
)
def test_binary_ops(op, expected):
    vm, _ = run(f"push 10\npush 3\n{op}")
    assert vm.stack == [expected]


def test_dup_swap_discard():
    vm, _ = run("push 1\npush 2\ndup")
    assert vm.stack == [1, 2, 2]
    vm, _ = run("push 1\npush 2\nswap")
    assert vm.stack == [2, 1]
    vm, _ = run("push 1\npush 2\ndiscard")
    assert vm.stack == [1]


def test_division_floors_toward_negative_infinity():
    vm, _ = run("push 7\npush 2\nsub\npush 0\nswap\nsub\npush 2\ndiv")
    # (0 - (7-2)) // 2 == -5 // 2 == -3
    assert vm.stack == [-3]


def test_stack_underflow():
    with pytest.raises(MCVRuntimeError, match="underflow"):
        run("add")


def test_division_by_zero():
    with pytest.raises(MCVRuntimeError, match="zero"):
        run("push 1\npush 0\ndiv")


def test_heap_store_and_retrieve():
    vm, _ = run("push 7\npush 99\nstore\npush 7\nretrieve")  # heap[7]=99
    assert vm.stack == [99]


def test_unset_heap_address_reads_zero():
    vm, _ = run("push 123\nretrieve")
    assert vm.stack == [0]


def test_output_char_and_number():
    _, out = run("push 65\noutchar\npush 66\noutchar\npush 42\noutnum")
    assert out == "AB42"


def test_jump_and_label():
    # jump over a push that would dirty the stack
    _, out = run("jmp V\npush 1\noutnum\nmark V\npush 9\noutnum")
    assert out == "9"


def test_jz_taken_and_not_taken():
    _, out = run("push 0\njz V\npush 1\noutnum\nmark V\npush 2\noutnum")
    assert out == "2"  # jz taken, skips the '1'
    _, out = run("push 5\njz V\npush 1\noutnum\nmark V")
    assert out == "1"  # jz not taken


def test_call_and_return():
    _, out = run(
        """
        call C
        push 8
        outnum
        end
        mark C
        push 7
        outnum
        ret
        """
    )
    assert out == "78"  # subroutine prints 7, returns, main prints 8


def test_undefined_label_errors():
    with pytest.raises(MCVRuntimeError, match="undefined label"):
        run("jmp V")


def test_duplicate_label_errors():
    with pytest.raises(MCVRuntimeError, match="more than once"):
        run("mark C\nmark C")


def test_return_without_call_errors():
    with pytest.raises(MCVRuntimeError, match="no matching call"):
        run("ret")


def test_readchar_eof_sentinel():
    vm, _ = run("push 0\nreadchar\npush 0\nretrieve", stdin="")
    assert vm.stack == [-1]


def test_readnum():
    vm, _ = run("push 0\nreadnum\npush 0\nretrieve", stdin="123\n")
    assert vm.stack == [123]
