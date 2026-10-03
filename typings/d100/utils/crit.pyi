from ..ast.dice import Dice as Dice
from ..ast.node import Number as Number
from ..enums import Critical as Critical

def determine_crit_type(root: Number, d20: Number | None) -> Critical: ...
