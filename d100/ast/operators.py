from typing import Literal

UnaryOperator = Literal["+", "-"]
BinaryOperator = Literal["+", "-", "*", "/", "//", "%", "<", ">", "==", ">=", "<=", "!="]

SetSelectorCategory = Literal["h", "l"]
ValueSelectorCategory = Literal["<", ">", "==", ">=", "<=", "!=", "", None]
SelectorCategory = SetSelectorCategory | ValueSelectorCategory

DiceCategory = Literal["rr", "ro", "ra", "rs", "e", "mi", "ma"]
SetCategory = Literal["k", "p"]
ExpressionCategory = Literal["red"]
AdvantageCategory = Literal["adv", "dis"]

OperatorCategory = DiceCategory | SetCategory | ExpressionCategory | AdvantageCategory


class SetSelector:
    cat: SetSelectorCategory
    num: int

    def __init__(self, cat: SetSelectorCategory, num: int) -> None:
        self.cat = cat
        self.num = int(num)

    def copy(self) -> "SetSelector":
        return SetSelector(self.cat, self.num)

    def __str__(self) -> str:
        if self.cat:
            return f"{self.cat}{self.num}"
        return str(self.num)

    def __repr__(self) -> str:
        return f"<SetSelector cat={self.cat} num={self.num} />"


class ValueSelector:
    cat: ValueSelectorCategory
    num: int

    def __init__(self, cat: ValueSelectorCategory, num: int) -> None:
        self.cat = cat
        self.num = int(num)

    def copy(self) -> "ValueSelector":
        return ValueSelector(self.cat, self.num)

    def __str__(self) -> str:
        if self.cat:
            return f"{self.cat}{self.num}"
        return str(self.num)

    def __repr__(self) -> str:
        return f"<ValueSelector cat={self.cat} num={self.num} />"

    def matches(self, value: int) -> bool:
        match self.cat:
            case None | "" | "==":
                return value == self.num

            case "!=":
                return value != self.num

            case "<":
                return value < self.num

            case "<=":
                return value <= self.num

            case ">":
                return value > self.num

            case ">=":
                return value >= self.num


Selector = SetSelector | ValueSelector


def SelectorNew(cat: ValueSelectorCategory | SetSelectorCategory, num: int) -> Selector:
    if cat == "h" or cat == "l":
        return SetSelector(cat, num)
    return ValueSelector(cat, num)


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

    def __repr__(self) -> str:
        sels = "".join(repr(sel) for sel in self.sels)
        return f"<Operator op={self.op} sels={sels} />"
