from typing import Literal

from d100 import parse, roll, utils
import pytest

from d100.errors import RollError

from d100.ast.expression import ASTExpression


def test_advantage_d20():
    r = roll("1d20")
    assert 1 <= r.total <= 20
    assert len(r.rolls) == 1
    assert len(r.warnings) == 0
    assert r.expression == "1d20"

    r = roll("1d20adv2")
    assert 1 <= r.total <= 20
    assert len(r.rolls) == 2
    assert len(r.warnings) == 0
    assert r.total == max(rr.total for rr in r.rolls)
    assert r.expression == "1d20adv2"

    r = roll("1d20adv3")
    assert 1 <= r.total <= 20
    assert len(r.rolls) == 3
    assert len(r.warnings) == 0
    assert r.total == max(rr.total for rr in r.rolls)
    assert r.expression == "1d20adv3"

    r = roll("1d20dis2")
    assert 1 <= r.total <= 20
    assert len(r.rolls) == 2
    assert len(r.warnings) == 0
    assert r.total == min(rr.total for rr in r.rolls)
    assert r.expression == "1d20dis2"

    expr = parse("1d20+1d20+6")
    r = roll(utils.add_advantage_to_d20_in_expression(expr, "adv", 2))
    assert 8 <= r.total <= 46
    assert len(r.rolls) == 2
    assert len(r.warnings) == 0
    assert r.expression == "1d20adv2 + 1d20 + 6"


# adv/dis should do nothing on non-d20s
def test_advantage_non_d20():
    with pytest.raises(RollError):
        expr = parse("1d6")
        utils.add_advantage_to_d20_in_expression(expr, "adv", 2)

    with pytest.raises(RollError):
        expr = parse("1d6")
        utils.add_advantage_to_d20_in_expression(expr, "dis", 2)


@pytest.mark.parametrize(
    "rolls,expr",
    [
        (2, "1d20+4"),
        (2, "4+1d20"),
        (2, "1d20+1d20*4"),
        (2, "1d20*4+1d20"),
        (4, "1d20+1d20adv"),
        (False, "1d20*4"),
        (False, "1d6"),
        (False, "4"),
    ],
)
def test_advantage_roll_count(rolls: int | Literal[False], expr: str | ASTExpression):
    expr = parse(expr)

    if not rolls:
        with pytest.raises(RollError):
            expr = utils.add_advantage_to_d20_in_expression(expr, "adv", 2)
    else:
        expr = utils.add_advantage_to_d20_in_expression(expr, "adv", 2)
        r = roll(expr)
        assert len(r.rolls) == rolls
        assert r.total == max(rr.total for rr in r.rolls)


@pytest.mark.parametrize("expr", [("1d20adv"), ("1d20dis"), ("1d6+1d20adv")])
def test_advantage_to_already_existing_fails(expr: str | ASTExpression):
    # if advantage is requested for an expression that already has advantage, a warning is thrown
    with pytest.raises(RollError):
        expr = parse(expr)
        utils.add_advantage_to_d20_in_expression(expr, "adv", 2)
