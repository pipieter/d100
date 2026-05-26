from typing import Literal

UnaryOperator = Literal["+", "-"]
BinaryOperator = Literal["+", "-", "*", "/", "//", "%", "<", ">", "==", ">=", "<=", "!="]
SelectorCategory = Literal["<", ">", "h", "l"]
OperatorCategory = Literal[
    # set only
    "k",
    "p",
    # dice only
    "rr",
    "ro",
    "ra",
    "rs",
    "e",
    "mi",
    "ma",
    # expr only
    "red",
    # advantage
    "adv",
    "dis",
]
AdvantageCategory = Literal["adv", "dis"]


class Selector:
    cat: SelectorCategory | None
    num: int

    def __init__(self, cat: SelectorCategory | None, num: int) -> None:
        self.cat = cat
        self.num = int(num)

    def copy(self) -> "Selector":
        return Selector(self.cat, self.num)

    def __str__(self) -> str:
        if self.cat:
            return f"{self.cat}{self.num}"
        return str(self.num)


class Operator:
    IMMEDIATE = {"mi", "ma"}

    op: OperatorCategory
    sels: list["Selector"]

    def __init__(self, op: OperatorCategory, sels: list["Selector"]):
        self.op = op
        self.sels = sels

    @classmethod
    def new(cls, op: OperatorCategory, sel: "Selector | None" = None) -> "Operator":
        """Create an operator from an op and a selector"""
        if sel is None:
            sels = []
        else:
            sels = [sel]
        return cls(op, sels)

    def add_sels(self, sels: list["Selector"]) -> None:
        """Add selectors to the operator."""
        self.sels.extend(sels)

    def copy(self) -> "Operator":
        sels = [sel.copy() for sel in self.sels]
        return Operator(self.op, sels)

    def __str__(self):
        if len(self.sels) == 0:
            return self.op
        return "".join([f"{self.op}{str(sel)}" for sel in self.sels])
