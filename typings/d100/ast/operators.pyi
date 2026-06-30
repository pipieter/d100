from _typeshed import Incomplete

UnaryOperator: Incomplete
BinaryOperator: Incomplete
SelectorCategory: Incomplete
OperatorCategory: Incomplete
AdvantageCategory: Incomplete

class Selector:
    cat: SelectorCategory | None
    num: int
    def __init__(self, cat: SelectorCategory | None, num: int) -> None: ...
    def copy(self) -> Selector: ...

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
