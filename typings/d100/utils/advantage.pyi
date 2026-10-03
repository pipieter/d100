from typing import Sequence, TypeVar

from ..ast.expression import ASTExpression as ASTExpression
from ..ast.node import Number as Number
from ..ast.operators import (
    AdvantageCategory as AdvantageCategory,
    Operator as Operator,
    OperatorCategory as OperatorCategory,
    Selector as Selector,
)
from ..distribution import Distribution as Distribution
from ..errors import RollError as RollError

TNumber = TypeVar("TNumber", bound=Number)

def add_advantage_to_d20_in_expression(expr: ASTExpression, adv: AdvantageCategory, count: int) -> ASTExpression:
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

def apply_advantage_to_distribution(distribution: Distribution, adv: OperatorCategory | None, num: int | None): ...
def find_from_advantage(rolls: Sequence[TNumber], adv: OperatorCategory | None) -> TNumber: ...
