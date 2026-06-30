import pytest

from d100 import parse
from d100.ast.unevaluated import ASTUnevaluated
from d100.errors import RollSyntaxError


@pytest.mark.parametrize("expr", ["1d20abc", "xyz", "1d4 * 100gp", "x + y"])
def test_unevaluated(expr: str):
    # Test with not allowing unevaluated
    with pytest.raises(RollSyntaxError):
        parse(expr, allow_unevaluated=False)

    # Test with allowing evaluated
    parsed = parse(expr, allow_unevaluated=True)
    nodes = parsed.flatten()
    unevaluated = [node for node in nodes if isinstance(node, ASTUnevaluated)]
    assert len(unevaluated) > 0
