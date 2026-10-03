from ..ast.binop import ASTBinOp as ASTBinOp
from ..ast.dice import ASTDice as ASTDice
from ..ast.die import DiceSize as DiceSize
from ..ast.node import ASTNode as ASTNode

def find_dice(expr: ASTNode, num: int, size: DiceSize) -> ASTDice | None: ...
def find_d20(expr: ASTNode) -> ASTDice | None: ...
