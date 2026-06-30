from .ast.dice import ASTDice as ASTDice, Dice as Dice
from .ast.expression import ASTExpression as ASTExpression
from .ast.node import Number as Number
from .ast.operators import AdvantageOperator as AdvantageOperator, Operator as Operator, Selector as Selector
from .enums import Critical as Critical
from .errors import RollError as RollError

def determine_crit_type(root: Number, d20: Number | None) -> Critical: ...
def add_advantage_to_d20_in_expression(expr: ASTExpression, adv: AdvantageOperator, count: int) -> ASTExpression:
    """
    Add advantage to the d20 in an expression. This does not add advantage to
    the whole expression, rather it searches for the first (viable) d20 in the
    expression and adds advantage to that dice, if it doesn't already have it.

    Args:
        expr (ASTExpression): The expression to add it in.
        adv (AdvantageCategory): The advantage to add. Either 'adv' or 'dis'.
        count (int): The amount of times to roll.

    Raises:
        RollError: In case advantage could not be added.

    Returns:
        ASTExpression: The resulting expression with the advantage.
    """
