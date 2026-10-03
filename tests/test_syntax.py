import pytest

from d100 import roll


@pytest.mark.parametrize(
    "expression",
    [
        "1d20",
        "3d12+4",
        "  3    +    1d4  ",
        "1 * 1 * 1 * 1 * 1",
        "1d8ro<=2",
        "(1d6)d6",
        "((((1d6)d6)d6)d6)d6",
    ],
)
def test_correct_syntax(expression: str):
    roll(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "1d",
        "3d12mi",
        "  *    1d4  ",
        "1 * 1 * 1 * 1 * 1 *",
        "(1d6)adv2d6"
        "1d(1d6)"
    ],
)
def test_incorrect_syntax(expression: str):
    with pytest.raises(Exception):
        roll(expression)
