import pytest

from d100 import parse
from d100.ast.dice import ASTDice


@pytest.mark.parametrize(
    "has_d20,expr",
    [
        (True, "1d20+3"),
        (True, "1d20+1d4+3"),
        (True, "1d10+1d20"),
        (True, "1d20+1d20"),
        (True, "(1d20+1d20)+3"),
        (True, "1d20+1d20mi2"),
        (True, "(1d20*1d20)+1d20mi2"),
        (True, "1d20mi2"),
        (True, "1d20mi2+1d20"),
        (False, "1d20*4"),
        (False, "2d20"),
    ],
)
def test_context_d20(has_d20: bool, expr: str):
    tree = parse(expr)
    d20 = tree.find_d20()

    if has_d20:
        assert d20 is not None
        assert isinstance(d20, ASTDice)
    else:
        assert d20 is None


@pytest.mark.parametrize(
    "is_comparison, expr",
    [
        (True, "1d20 > 3"),
        (True, "1d20 - 1d4> 3"),
        (True, "((1d20 > 4))"),
        (False, "1d20"),
        (False, "(1d20 > 3) * 4"),
    ],
)
def test_is_comparison(is_comparison: bool, expr: str):
    tree = parse(expr)
    assert tree.is_comparison == is_comparison
