from typing import Literal

UnaryOperator = Literal["+", "-"]
BinaryOperator = Literal["+", "-", "*", "/", "//", "%", "<", ">", "==", ">=", "<=", "!="]
SelectorCategory = Literal["h", "l", "<", ">", "==", ">=", "<=", "!=", "", None]

DiceCategory = Literal["rr", "ro", "ra", "rs", "e", "mi", "ma"]
SetCategory = Literal["k", "p"]
ExpressionCategory = Literal["red"]
AdvantageCategory = Literal["adv", "dis"]

OperatorCategory = DiceCategory | SetCategory | ExpressionCategory | AdvantageCategory


class Selector:
    cat: SelectorCategory
    num: int

    def __init__(self, cat: SelectorCategory, num: int) -> None:
        self.cat = cat
        self.num = int(num)

    def copy(self) -> "Selector":
        return Selector(self.cat, self.num)

    def __str__(self) -> str:
        if self.cat:
            return f"{self.cat}{self.num}"
        return str(self.num)

    def __repr__(self) -> str:
        return f"<ValueSelector cat={self.cat} num={self.num} />"

    def can_match(self, _: int) -> bool:
        return self.cat not in ["h", "l"]

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

            case "h" | "l":
                raise ValueError(f"Cannot apply matches to {str(self)}")


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
