from .ast.dice import ASTDice as ASTDice, Dice as Dice
from .ast.node import Number as Number
from .ast.operators import AdvantageCategory as AdvantageCategory, Operator as Operator, Selector as Selector
from .enums import Critical as Critical

def determine_crit_type(root: Number, d20: Number | None) -> Critical: ...
def add_adv_operator_to_dice(dice: ASTDice, adv: AdvantageCategory | None, count: int) -> bool: ...
