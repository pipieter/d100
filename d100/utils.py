from .ast.dice import ASTDice, Dice
from .ast.node import Number
from .ast.operators import AdvantageCategory, Operator, Selector
from .enums import Critical


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


def add_adv_operator_to_dice(dice: ASTDice, adv: AdvantageCategory | None, count: int) -> bool:
    if adv is None:
        return True

    # Check if the dice already has adv or dis
    for operator in dice.operations:
        if operator.op in ["adv", "dis"]:
            return False

    dice.operations.append(Operator(adv, [Selector(None, count)]))
    return True
