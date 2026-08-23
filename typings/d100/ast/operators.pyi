from _typeshed import Incomplete

UnaryOperator: Incomplete
BinaryOperator: Incomplete
SetSelectorCategory: Incomplete
ValueSelectorCategory: Incomplete
SelectorCategory = SetSelectorCategory | ValueSelectorCategory
DiceCategory: Incomplete
SetCategory: Incomplete
ExpressionCategory: Incomplete
AdvantageCategory: Incomplete
OperatorCategory = DiceCategory | SetCategory | ExpressionCategory | AdvantageCategory

class SetSelector:
    cat: SetSelectorCategory
    num: int
    def __init__(self, cat: SetSelectorCategory, num: int) -> None: ...
    def copy(self) -> SetSelector: ...

class ValueSelector:
    cat: ValueSelectorCategory
    num: int
    def __init__(self, cat: ValueSelectorCategory, num: int) -> None: ...
    def copy(self) -> ValueSelector: ...
    def matches(self, value: int) -> bool: ...

Selector = SetSelector | ValueSelector

def SelectorNew(cat: ValueSelectorCategory | SetSelectorCategory, num: int) -> Selector: ...

class Operator:
    IMMEDIATE: Incomplete
    op: OperatorCategory
    sels: list["Selector"]
    def __init__(self, op: OperatorCategory, sels: list["Selector"]) -> None: ...
    @classmethod
    def new(cls, op: OperatorCategory, sel: Selector | None = None) -> Operator:
        """Create an operator from an op and a selector"""
    def add_sels(self, sels: list["Selector"]) -> None:
        """Add selectors to the operator."""
    def copy(self) -> Operator: ...
