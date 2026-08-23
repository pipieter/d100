"""
This test file is to ensure the two builders in d20distribution,
ConvolutionDistributionBuilder and DiscreteDistributionBuilder, have the same
end distributions.
"""

from collections.abc import Sequence

import pytest

from d100.ast.operators import Operator, OperatorCategory, Selector, SelectorCategory
from d100.distribution import (
    ConvolutionDistributionBuilder,
    DiscreteDistributionBuilder,
)
from . import approx


def operator(op: OperatorCategory, sel: tuple[SelectorCategory | None, int]):
    cat, num = sel
    return Operator(op, Selector(cat, num))


@pytest.mark.parametrize("count", [1, 2, 3, 4])
@pytest.mark.parametrize("sides", [4, 6, 8, 12])
@pytest.mark.parametrize(
    "operators",
    [
        [operator("ma", (None, 4))],
        [operator("mi", (None, 2))],
        [operator("k", (None, 4))],
        [operator("p", (None, 4))],
        [operator("k", ("<", 4))],
        [operator("p", ("<", 4))],
        [operator("k", (">", 4))],
        [operator("p", (">", 4))],
        [operator("rr", (None, 4))],
        [operator("rr", ("<", 4))],
        [operator("rr", (">", 4))],
        [operator("ro", (None, 4))],
        [operator("ro", ("<", 4))],
        [operator("ro", (">", 4))],
        [operator("p", ("<", 3)), operator("rr", (">", 4))],
        [operator("rr", (">", 4)), operator("p", ("<", 3))],
        [operator("p", ("<", 3)), operator("ro", (">", 4))],
        [operator("k", (None, 3)), operator("mi", (None, 2))],
        [operator("mi", (None, 2)), operator("k", (">", 3))],
    ],
)
def test_builders(count: int, sides: int, operators: Sequence[Operator]):
    convolution = ConvolutionDistributionBuilder(count, sides, operators).distribution()
    discrete = DiscreteDistributionBuilder(count, sides, operators).distribution()

    assert convolution.keys() == discrete.keys()

    for key in convolution.keys():
        assert convolution.get(key) == approx(discrete.get(key), 1e-6)
