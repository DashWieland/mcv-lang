"""Integration tests: run the shipped example programs and check their output."""

import io
from pathlib import Path

import pytest

from mcv import lex
from mcv.vm import VM

EXAMPLES = Path(__file__).parent.parent / "examples"


def run_example(name, stdin=""):
    source = (EXAMPLES / name).read_text().strip()
    out = io.StringIO()
    VM(lex(source), stdin=io.StringIO(stdin), stdout=out).run()
    return out.getvalue()


def test_hello():
    assert run_example("hello.mcv") == "Hello, World!\n"


def test_fibonacci():
    assert run_example("fibonacci.mcv") == "0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n"


@pytest.mark.parametrize("text", ["", "Babel", "M C V\n410 pages"])
def test_cat_echoes_input(text):
    assert run_example("cat.mcv", stdin=text) == text


def test_truth_machine_zero():
    assert run_example("truth_machine.mcv", stdin="0\n") == "0"


def test_truth_machine_one_loops():
    # The 1-branch never halts; cap it with a stop-after-N stdout.
    class Stop(io.StringIO):
        def write(self, s):
            super().write(s)
            if len(self.getvalue()) >= 6:
                raise StopIteration

    source = (EXAMPLES / "truth_machine.mcv").read_text().strip()
    out = Stop()
    with pytest.raises(StopIteration):
        VM(lex(source), stdin=io.StringIO("1\n"), stdout=out).run()
    assert out.getvalue() == "111111"
