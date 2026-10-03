from ..ast.dice import Dice
from ..ast.node import Number
from ..enums import Critical


def determine_crit_type(root: Number, d20: Number | None) -> Critical:
    if isinstance(d20, Dice):
        dice = d20.keptset
    else:
        return Critical.NONE

    if len(dice) != 1 or d20.size != 20:
        return Critical.NONE

    if dice[0].value == 1:
        return Critical.FAIL

    if dice[0].value == 20:
        return Critical.CRIT

    if root.total == 20 and dice[0].value != 20:
        return Critical.DIRTY

    return Critical.NONE

