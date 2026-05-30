import pytest

from mcv.asm import assemble, encode_number
from mcv.errors import MCVSyntaxError
from mcv.lexer import Instr, lex


def names(src):
    return [i.name for i in lex(src)]


def test_each_instruction_decodes():
    src = assemble(
        """
        push 0
        dup
        swap
        discard
        add
        sub
        mul
        div
        mod
        mark M
        call M
        jmp M
        jz M
        jneg M
        ret
        store
        retrieve
        outchar
        outnum
        readchar
        readnum
        end
        """
    )
    assert names(src) == [
        "PUSH", "DUP", "SWAP", "DISCARD",
        "ADD", "SUB", "MUL", "DIV", "MOD",
        "MARK", "CALL", "JMP", "JZ", "JNEG", "RET",
        "STORE", "RETRIEVE",
        "OUTCHAR", "OUTNUM", "READCHAR", "READNUM",
        "END",
    ]


def test_discard_is_literally_MCV():
    assert assemble("discard") == "MCV"
    assert lex("MCV") == [Instr("DISCARD")]


@pytest.mark.parametrize("n", [0, 1, 2, 5, 42, -1, -7, 1000, -1000, 2**40])
def test_number_roundtrip(n):
    src = "MM" + encode_number(n)  # PUSH <n>
    assert lex(src) == [Instr("PUSH", n)]


def test_negative_zero_is_zero():
    assert lex("MM" + "CV") == [Instr("PUSH", 0)]  # sign C (-), no digits


def test_labels_are_three_chars():
    instr = lex(assemble("mark CMV"))[0]
    assert instr == Instr("MARK", "CMV")


def test_illegal_character():
    with pytest.raises(MCVSyntaxError):
        lex("MMXCV")


def test_truncated_number_errors():
    with pytest.raises(MCVSyntaxError):
        lex("MMMC")  # PUSH, sign, a digit, but no V terminator


def test_truncated_label_errors():
    with pytest.raises(MCVSyntaxError):
        lex("VMMMC")  # MARK + only two label chars


def test_unknown_arithmetic_opcode_errors():
    with pytest.raises(MCVSyntaxError):
        lex("CMVC")  # IMP=CM (arith) then VC is not a valid op


def test_empty_program_is_empty_list():
    assert lex("") == []
