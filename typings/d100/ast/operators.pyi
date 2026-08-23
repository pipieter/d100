from _typeshed import Incomplete

UnaryOperator: Incomplete
BinaryOperator: Incomplete
SelectorCategory: Incomplete
DiceCategory: Incomplete
SetCategory: Incomplete
ExpressionCategory: Incomplete
AdvantageCategory: Incomplete
OperatorCategory = DiceCategory | SetCategory | ExpressionCategory | AdvantageCategory

class Selector:
    cat: SelectorCategory
    num: int
    def __init__(self, cat: SelectorCategory, num: int) -> None: ...
    def copy(self) -> Selector: ...
    def can_match(self, _: int) -> bool: ...
    def matches(self, value: int) -> bool: ...

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
