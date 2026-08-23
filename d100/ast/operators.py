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
    sels: Selector

    def __init__(self, op: OperatorCategory, sel: Selector):
        self.op = op
        self.sel = sel

    @classmethod
    def new(cls, op: OperatorCategory, sel: "Selector | None" = None) -> "Operator":
        """Create an operator from an op and a selector"""
        if sel is None:
            sel = Selector(None, -1)
        return cls(op, sel)

    def copy(self) -> "Operator":
        return Operator(self.op, self.sel.copy())

    def __str__(self):
        # Specific null operator case
        if self.sel.cat is None and self.sel.num < 0:
            return self.op
        return f"{self.op}{str(self.sel)}"

    def __repr__(self) -> str:
        return f"<Operator op={self.op} sel={repr(self.sel)} />"
