import abc
import copy
import itertools
import math
from collections import defaultdict
from collections.abc import Sequence
from typing import Callable, Iterable, Optional

import numpy as np

from .ast.operators import Operator, Selector
from .errors import RollError


def _combine_dictionaries(
    a: dict[int, float], b: dict[int, float], func: Callable[[int, int], int]
) -> dict[int, float]:
    """Combine two dictionaries by combining their keys pair-wise using a combination function.

    Args:
        a (dict[int, float]): The first dictionary to merge.
        b (dict[int, float]): The second dictionary to merge.
        func (Callable[[int, int], int]): A function to combine keys. This function should return a new valid key.

    Returns:
        dict[int, float]: The combined dictionary.
    """

    result = dict[int, float]()
    for ka, va in a.items():
        for kb, vb in b.items():
            key = func(ka, kb)
            result[key] = result.get(key, 0) + va * vb
    return result


class Distribution(object):
    _dist: dict[int, float]

    def __init__(self, values: Optional[dict[int, float]] = None):
        if values:
            self._dist = copy.deepcopy(values)
        else:
            self._dist = {0: 1.0}

    def keys(self) -> Iterable[int]:
        """Get the possible dice sums of the distribution.

        Returns:
            Iterable[int]: The possible dice sums of the distribution sorted from lowest to highest.
        """
        return list(sorted(list(self._dist.keys())))

    def values(self) -> Iterable[float]:
        """Get all stored probability values of the distribution.

        Returns:
            Iterable[float]: The possible probability values of the distribution, in no particular order.
        """
        return list(self._dist.values())

    def get(self, key: int) -> float:
        """Get the probability of a single key.

        Args:
            key (int): The key to retrieve.

        Returns:
            float: The stored probability of the key, or zero if the key is not present.
        """

        return self._dist.get(key, 0)

    def get_at_least(self, key: int) -> float:
        """Get the probability of getting at least the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at least the key, inclusive of the key.
        """
        keys = [k for k in self.keys() if k >= key]
        if len(keys) == 0:
            return 0
        return sum(self.get(k) for k in keys)

    def get_at_most(self, key: int) -> float:
        """Get the probability of getting at most the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at most the key, inclusive of the key.
        """
        keys = [k for k in self.keys() if k <= key]
        if len(keys) == 0:
            return 0
        return sum(self.get(k) for k in keys)

    def min(self) -> int:
        """Get the minimum key in the distribution.

        Returns:
            int: The lowest key in the distribution.
        """

        return min(self.keys())

    def max(self) -> int:
        """Get the maximum key in the distribution.

        Returns:
            int: The highest key in the distribution.
        """
        return max(self.keys())

    def mean(self, key_mapping: Optional[Callable[[int], int]] = None) -> float:
        """Get the mean value of the distribution.

        Args:
            mapping (Optional[Callable[[int], int]], optional): An optional function to perform on the keys of the distribution. Defaults to None.

        Returns:
            float: The mean of the distribution.
        """

        if key_mapping is None:
            key_mapping = lambda x: x
        return sum([key_mapping(key) * probability for key, probability in self._dist.items()])

    def stdev(self) -> float:
        """Get the standard deviation of the distribution.

        Returns:
            float: The standard deviation of the distribution.
        """
        # variance = E(X^2) - E(X)^2
        # stdev = sqrt(variance)
        e_x2 = self.mean(key_mapping=lambda x: x**2)
        ex_2 = self.mean() ** 2
        return math.sqrt(abs(e_x2 - ex_2))

    def __add__(self, other: "Distribution") -> "Distribution":
        """Adds two distributions together, e.g. 1d20 + 1d4.

        Args:
            other (Distribution): The other distribution to add.

        Returns:
            Distribution: The sum of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a + b))

    def __sub__(self, other: "Distribution") -> "Distribution":
        """Subtract two distributions from each other, e.g. 1d20 - 1d4.

        Args:
            other (Distribution): The other distribution to subtract.

        Returns:
            Distribution: The difference of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a - b))

    def __mul__(self, other: "Distribution") -> "Distribution":
        """Multiply two distributions together, e.g. 1d20 * 1d4.

        Args:
            other (Distribution): The other distribution to multiply.

        Returns:
            Distribution: The product of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a * b))

    def __floordiv__(self, other: "Distribution") -> "Distribution":
        """Divide two distributions from each other, e.g. 1d20 / 1d4. Note that this is the floor
        division, and not the true division, as distribution keys need to be integers.

        Args:
            other (Distribution): The divisor of the division.

        Raises:
            ZeroDivisionError: When one of the possible keys in the divisor is zero.

        Returns:
            Distribution: The division of the two distributions.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a // b))

    def __mod__(self, other: "Distribution") -> "Distribution":
        """Use the modulo operator on two distributions, e.g. 1d20 % 1d8.

        Args:
            other (Distribution): The other distribution for the modulo operator.

        Returns:
            Distribution: The resulting modulo operator.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: a % b))

    def __lt__(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the less than operator, e.g. 1d6 < 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting less than comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a < b)))

    def __le__(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the less than or equal operator, e.g. 1d6 <= 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting less than or equal comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a <= b)))

    def __gt__(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the greater than operator, e.g. 1d6 > 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting greater than comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a > b)))

    def __ge__(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the greater or equal than operator, e.g. 1d6 >= 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting greater or equal than comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a >= b)))

    def equals(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the equality operator, e.g. 1d6 == 1d8.

        Args:
            other (Distribution): The other distribution in the comparison

        Returns:
            Distribution: The resulting equality comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a == b)))

    def not_equals(self, other: "Distribution") -> "Distribution":
        """Compare two distributions using the inequality operator, e.g. 1d6 != 1d8.

        Args:
            other (Distribution): The other distribution in the comparison

        Returns:
            Distribution: The resulting inequality comparison.
        """
        return Distribution(_combine_dictionaries(self._dist, other._dist, lambda a, b: int(a != b)))

    def __neg__(self) -> "Distribution":
        """Negate the values of a distribution.

        Returns:
            Distribution: The distribution with the signs of all of its keys reversed.
        """
        return Distribution({-v: k for v, k in self._dist.items()})

    def advantage(self, count: int = 2) -> "Distribution":
        """Calculate the advantage of a distribution. This means that for all possible
        keys in the distribution, a pairwise combination is taken where the highest value
         is taken.

        Args:
            count (int, optional): The amount of dice to be rolled for which the highest
            is taken. For example, if count is three then three dice are rolled and the
            highest is taken. Defaults to 2.

        Raises:
            InvalidOperationError: If less than one dice count is given.

        Returns:
            Distribution: The distribution rolled multiple times, with the highest values
            taken each time.
        """
        if count < 1:
            raise RollError(f"Rolling with advantage requires at least one roll, instead received {count}.")

        result = copy.copy(self._dist)
        for _ in range(1, count):
            result = _combine_dictionaries(result, self._dist, lambda a, b: max(a, b))
        return Distribution(result)

    def disadvantage(self, count: int = 2) -> "Distribution":
        """Calculate the disadvantage of a distribution. This means that for all possible
        keys in the distribution, a pairwise combination is taken where the lowest value
         is taken.

        Args:
            count (int, optional): The amount of dice to be rolled for which the lowest
            is taken. For example, if count is three then three dice are rolled and the
            lowest is taken. Defaults to 2.

        Raises:
            InvalidOperationError: If less than one dice count is given.

        Returns:
            Distribution: The distribution rolled multiple times, with the lowest values
            taken each time.
        """

        if count < 1:
            raise RollError(f"Rolling with disadvantage requires at least one roll, instead received {count}.")

        result = copy.copy(self._dist)
        for _ in range(1, count):
            result = _combine_dictionaries(result, self._dist, lambda a, b: min(a, b))
        return Distribution(result)

    def __copy__(self) -> "Distribution":
        """Create a copy of the distribution. All values of the other distribution
        are deep-copied.

        Returns:
            Distribution: A copy of the distribution.
        """
        return Distribution(self._dist)

    def __deepcopy__(self) -> "Distribution":
        """Creates a deep copy of the distribution.

        Returns:
            Distribution: A deep copy of the distribution.
        """
        return Distribution(copy.deepcopy(self._dist))


class AbstractDistributionBuilder(abc.ABC):
    """An abstract class used to build distributions."""

    @abc.abstractmethod
    def distribution(self) -> Distribution:
        """Build the distribution based on the builder.

        Returns:
            Distribution: The distribution object matching the current state of the distribution.
        """
        ...

    def apply_operation(self, op: Operator) -> None:
        """Apply a valid operator to the current distribution. This internally  changes the
        state of the builder

        Args:
            op (Operator): The operator to be applied.

        Raises:
            RollError: When the operation in question is unknown or not supported.
        """
        operation_functions = {
            "mi": self.apply_mi,
            "ma": self.apply_ma,
            "ro": self.apply_ro,
            "e": self.apply_e,
            "k": self.apply_k,
            "p": self.apply_p,
            "ra": self.apply_ra,
            "rr": self.apply_rr,
        }

        operation: str = op.op
        selectors: list[Selector] = op.sels

        if operation not in operation_functions:
            raise RollError(f"Unsupported operator: '{op.op}'")

        operation_functions[operation](selectors)

    @abc.abstractmethod
    def apply_mi(self, selectors: list[Selector]) -> None:
        """Apply the minimum operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `mi` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ma(self, selectors: list[Selector]) -> None:
        """Apply the maximum operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ma` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ro(self, selectors: list[Selector]) -> None:
        """Apply the re-roll once operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ro` operator.
        """
        ...

    @abc.abstractmethod
    def apply_e(self, selectors: list[Selector]) -> None:
        """Apply the explode operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `e` operator.
        """
        ...

    @abc.abstractmethod
    def apply_k(self, selectors: list[Selector]) -> None:
        """Apply the keep operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `k` operator.
        """
        ...

    @abc.abstractmethod
    def apply_p(self, selectors: list[Selector]) -> None:
        """Apply the drop operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `p` operator.
        """
        ...

    @abc.abstractmethod
    def apply_ra(self, selectors: list[Selector]) -> None:
        """Apply the reroll and add operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ra` operator.
        """
        ...

    @abc.abstractmethod
    def apply_rr(self, selectors: list[Selector]) -> None:
        """Apply the repeated reroll operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `rr` operator.
        """
        ...

    @staticmethod
    def _matches_selector(value: int, selector: Selector) -> bool:
        """Checks if a given value matches a selector. Only works for selectors that are applied to single elements.

        Args:
            value (int): The value to be matched.
            selector (Selector): The selector used for matching.

        Raises:
            RollError: When an invalid selector is given or when a selector is given that applies to a set of elements.

        Returns:
            bool: Whether the value matched the selector.
        """
        cat: str | None = selector.cat

        if cat in ["", None]:
            return value == selector.num

        if cat == "<":
            return value < selector.num

        if cat == ">":
            return value > selector.num

        raise RollError(f"Invalid operation found between value '{value}' and '{str(selector)}'")

    @staticmethod
    def _creates_infinite_rr_loop(count: int, sides: int, selector: Selector) -> bool:
        """Check if a selector would cause an infinite loop when matched with the rr modifier.

        Args:
            count (int): The amount of dice.
            sides (int): The amount of sides of each die.
            selector (Selector): The selector used for the rr operation modifier.

        Returns:
            bool: Whether the selector would create an infinite loop.
        """
        if count == 0:
            return False

        # e.g. 1d6rrl1
        if selector.cat in ["h", "l"]:
            return selector.num > 0

        # e.g. 1d6rr<7
        if selector.cat == "<" and sides < selector.num:
            return True

        # e.g. 1d6rr>0
        if selector.cat == ">" and selector.num == 0:
            return True

        # Specific case, re-rolling a one on a one-sided die, 1d1rr1
        if sides == 1 and selector.cat in [None, ""] and selector.num == 1:
            return True

        return False


class ConvolutionDistributionBuilder(AbstractDistributionBuilder):
    """
    A distribution builder that internally uses convolutions to calculate the distribution.
    These convolutions are typically much faster than iterating over all possibilities, but
    they are more limited in the operations they can perform.

    For more information on how convolutions work, see this blog post:
    https://blog.demofox.org/2025/01/05/dice-deconvolution-and-generating-functions/


    Raises:
        RollError: When an invalid operator is passed as an argument. Certain operations are not possible using convolutions.
    """

    _count: int
    _sides: int
    _convolution: list[float]

    def __init__(self, count: int, sides: int, operations: Sequence[Operator]) -> None:
        """Create a convolution distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[Operator]): A list of operators to be applied to the expression.
        """
        super().__init__()
        self._count = count
        self._sides = sides
        self._convolution = [0] + [1 / sides] * sides

        for operation in operations:
            self.apply_operation(operation)

    def distribution(self) -> Distribution:
        result = np.array([1.0])
        convolution = np.array(self._convolution)
        for _ in range(self._count):
            result = np.convolve(result, convolution)

        dist = {k: float(v) for k, v in enumerate(result) if abs(v) >= 1e-10}
        return Distribution(dist)

    @staticmethod
    def supports_operation(operation: Operator) -> bool:
        """Checks if the ConvolutionDistributionBuilder supports an operation.

        Args:
            operation (Operator): The operation to be checked.

        Returns:
            bool: Whether the operation is supported.
        """
        invalid_operations = ["e", "ra"]
        invalid_selector_categories = ["h", "l"]

        if operation.op in invalid_operations:
            return False

        categories = [sel.cat for sel in operation.sels]
        if any(category in invalid_selector_categories for category in categories):
            return False

        return True

    def apply_mi(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise RollError(f"Unsupported selector category for mi: '{selector.cat}'")

            num: int = selector.num

            # Extend the convolution
            padding = num - len(self._convolution) + 1
            self._convolution.extend([0] * padding)
            for i in range(1, num):
                self._convolution[num] += self._convolution[i]
                self._convolution[i] = 0

    def apply_ma(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            if selector.cat not in ["", None]:
                raise RollError(f"Unsupported selector category for ma: '{selector.cat}'")

            num: int = selector.num
            for i in range(num + 1, len(self._convolution)):
                self._convolution[num] += self._convolution[i]
                self._convolution[i] = 0

    def apply_k(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            for i in range(1, len(self._convolution)):
                if not self._matches_selector(i, selector):
                    self._convolution[0] += self._convolution[i]
                    self._convolution[i] = 0

    def apply_p(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            for i in range(1, len(self._convolution)):
                if self._matches_selector(i, selector):
                    self._convolution[0] += self._convolution[i]
                    self._convolution[i] = 0

    def apply_ro(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            reroll = 1 / self._sides
            odds_rerolling = 0

            # Calculate the odds of event occurring
            for i in range(1, len(self._convolution)):
                if self._matches_selector(i, selector):
                    odds_rerolling += self._convolution[i]

            # Re-calculate the odds
            for i in range(1, len(self._convolution)):
                if self._matches_selector(i, selector):
                    self._convolution[i] = odds_rerolling * reroll
                else:
                    self._convolution[i] += odds_rerolling * reroll

    def apply_e(self, selectors: list[Selector]) -> None:
        raise RollError(f"Explode operator not supported for ConvolutionDistributionBuilder")

    def apply_ra(self, selectors: list[Selector]) -> None:
        raise RollError(f"Reroll and add operator not supported for ConvolutionDistributionBuilder")

    def apply_rr(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            if self._creates_infinite_rr_loop(self._count, self._sides, selector):
                raise RollError(
                    f"Selector {str(selector)} will result in an infinite rr reroll loop for"
                    f" {self._count}d{self._sides}!"
                )

            # In order to calculate the re-roll odds, we first find all the values that would be re-rolled,
            # and then we equally distribute the total probabilities of those rolls to all the values in the
            # range [1, sides].
            matched_values: list[int] = []
            target_values: list[int] = []

            for i in range(1, len(self._convolution)):
                if self._matches_selector(i, selector):
                    matched_values.append(i)
                elif i <= self._sides:
                    target_values.append(i)

            if len(target_values) == 0:
                raise RollError(f"Selector {str(selector)} could not be re-rolled for {self._count}d{self._sides}!")

            total_probability = sum(self._convolution[i] for i in matched_values)
            probability_per_target = total_probability / len(target_values)
            for value in matched_values:
                self._convolution[value] = 0
            for value in target_values:
                self._convolution[value] += probability_per_target


# Internal representation of a discrete key, which is a tuple of ints
DiscreteKey = tuple[int, ...]


class DiscreteDistributionBuilder(AbstractDistributionBuilder):
    _count: int
    _sides: int
    _dist: defaultdict[DiscreteKey, float]

    def __init__(self, count: int, sides: int, operations: Sequence[Operator]) -> None:
        """Create a discrete distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[Operator]): A list of operators to be applied to the expression.
        """
        super().__init__()
        self._count = count
        self._sides = sides
        self._dist = defaultdict(float)

        # Build distribution
        for raw_key in itertools.product(range(1, sides + 1), repeat=count):
            key = self._sort_key(raw_key)
            self._dist[key] += 1

        # Normalize the distribution
        total = sum(self._dist.values())
        for key in self._dist:
            self._dist[key] = self._dist[key] / total
        assert abs(sum(self._dist.values()) - 1) < 1e-8

        for operation in operations:
            self.apply_operation(operation)

    def distribution(self) -> Distribution:
        dist = defaultdict[int, float](float)
        for key, value in self._dist.items():
            dist[sum(key)] += value
        return Distribution(dict(dist))

    @staticmethod
    def _sort_key(key: DiscreteKey) -> DiscreteKey:
        """Sort a key in order to ensure consistency within the dictionary and improve performance.

        Args:
            key (DiscreteKey): The key to be sorted.

        Returns:
            DiscreteKey: The sorted key.
        """
        return tuple(sorted(key))

    def _transform_keys(self, transform: Callable[[DiscreteKey], DiscreteKey]) -> None:
        """Transform the internal keys based on a transform function. If the function would map multiple keys
        to the same new key, the old keys' probabilities will be added up for the probability of the new key.

        Args:
            transform (Callable[[DiscreteKey], DiscreteKey]): A transform function that transform a key into another key.
        """
        new_dist = defaultdict[DiscreteKey, float](float)
        for key, value in self._dist.items():
            new_key = transform(key)
            new_key = self._sort_key(new_key)
            new_dist[new_key] += value
        self._dist = new_dist

    def apply_mi(self, selectors: list[Selector]) -> None:
        def apply_mi_to_key(key: DiscreteKey, min_value: int) -> DiscreteKey:
            return tuple([value if value >= selector.num else min_value for value in key])

        for selector in selectors:
            if selector.cat not in ["", None]:
                raise RollError(f"Unsupported selector category for mi: '{selector.cat}'")

            min_value: int = selector.num
            self._transform_keys(lambda key: apply_mi_to_key(key, min_value))

    def apply_ma(self, selectors: list[Selector]) -> None:
        def apply_ma_to_key(key: DiscreteKey, max_value: int) -> DiscreteKey:
            return tuple([value if value <= selector.num else max_value for value in key])

        for selector in selectors:
            if selector.cat not in ["", None]:
                raise RollError(f"Unsupported selector category for ma: '{selector.cat}'")

            max_value: int = selector.num
            self._transform_keys(lambda key: apply_ma_to_key(key, max_value))

    def apply_k(self, selectors: list[Selector]) -> None:
        def apply_k_to_key(key: DiscreteKey, selector: Selector) -> DiscreteKey:
            if selector.cat is None:
                # Keep all values matching exactly selector.num
                return tuple([p for p in key if p == selector.num])

            if selector.cat == "<":
                # Keep all values smaller than selector.num
                return tuple([p for p in key if p < selector.num])

            if selector.cat == ">":
                # Keep all values greater than selector.num
                return tuple([p for p in key if p > selector.num])

            if selector.cat == "l":
                # Keep lowest selector.num values
                key = tuple(sorted(list(key), reverse=False))
                key = key[: selector.num]
                return key

            if selector.cat == "h":
                # Keep highest selector.num values
                key = tuple(sorted(list(key), reverse=True))
                key = key[: selector.num]
                return key

            raise RollError(f"Invalid keep modifier selector '{selector.cat}'.")

        for selector in selectors:
            self._transform_keys(lambda key: apply_k_to_key(key, selector))

    def apply_p(self, selectors: list[Selector]) -> None:
        def apply_p_to_key(key: DiscreteKey, selector: Selector) -> DiscreteKey:
            if selector.cat is None:
                # Drop all values matching exactly selector.num
                return tuple([p for p in key if p != selector.num])

            if selector.cat == "<":
                # Drop all values smaller than selector.num
                return tuple([p for p in key if p >= selector.num])

            if selector.cat == ">":
                # Drop all values greater than selector.num
                return tuple([p for p in key if p <= selector.num])

            if selector.cat == "l":
                # Drop lowest selector.num values
                key = tuple(sorted(list(key), reverse=False))
                key = key[selector.num :]
                return key

            if selector.cat == "h":
                # Drop highest selector.num values
                key = tuple(sorted(list(key), reverse=True))
                key = key[selector.num :]
                return key

            raise RollError(f"Invalid drop modifier selector '{selector.cat}'.")

        for selector in selectors:
            self._transform_keys(lambda key: apply_p_to_key(key, selector))

    def apply_ro(self, selectors: list[Selector]) -> None:
        def get_reroll_dice_possibilities(
            dice: DiscreteKey, sides: int, category: str | None, num: int
        ) -> list[DiscreteKey]:
            """
            Get all re-roll possibilities in a dice. This generates all possible results where the values matching
            the selector are re-rolled.
            """
            if len(dice) == 0:
                return [()]

            # Handle h and l separately, as they depend on the dice ordering
            if category in ["h", "l"]:
                if num <= 0:
                    return [dice]

                if category == "h":
                    dice = tuple(sorted(dice, reverse=True))
                else:
                    dice = tuple(sorted(dice, reverse=False))

                _, *rest = dice
                combinations = get_reroll_dice_possibilities(tuple(rest), sides, category, num - 1)
                outcomes: list[DiscreteKey] = []

                for combination in combinations:
                    for roll in range(1, sides + 1):
                        outcomes.append((roll,) + combination)

                return outcomes

            first, *rest = dice
            combinations = get_reroll_dice_possibilities(tuple(rest), sides, category, num)
            outcomes = []

            if (
                (category is None and first == num)
                or (category == ">" and first > num)
                or (category == "<" and first < num)
            ):
                for combination in combinations:
                    for roll in range(1, sides + 1):
                        outcomes.append((roll,) + combination)
            else:
                for combination in combinations:
                    outcomes.append((first,) + combination)

            return outcomes

        for selector in selectors:
            new_dist = defaultdict[DiscreteKey, float](float)
            for key in self._dist:
                odds = self._dist.get(key, 0)
                rerolls = get_reroll_dice_possibilities(key, self._sides, selector.cat, selector.num)
                for reroll in rerolls:
                    reroll_key = self._sort_key(reroll)
                    reroll_odds = odds / len(rerolls)
                    new_dist[reroll_key] += reroll_odds

            # Assert that the new distribution is also normalized
            assert abs(sum(new_dist.values()) - 1) < 1e-6

            self._dist = new_dist

    def apply_e(self, selectors: list[Selector]) -> None:
        def should_explode(selector: Selector, value: int) -> bool:
            if selector.cat is None:
                return value == selector.num
            if selector.cat == ">":
                return value > selector.num
            if selector.cat == "<":
                return value < selector.num

            raise RollError(f"Invalid explode modifier selector '{selector.cat}'.")

        def apply_explode(
            dist: defaultdict[DiscreteKey, float],
            selector: Selector,
            base_odds: float,
            base_key: DiscreteKey,
            cutoff: float = 1e-8,
        ) -> defaultdict[DiscreteKey, float]:
            """
            Recursively applies the explode operator to a single distribution to get the distribution
            of the exploded dice.

            Args:
                dist (defaultdict[DiscreteKey, float]): The original distribution
                selector (Selector): The exploding criteria
                base_odds (float): The base odds of the current distribution. Should be initialized as 1.0.
                base_key (DiscreteKey): The base key. Should be initialized as ().
                cutoff (float, optional): The cut-off point after which explode is no longer applied. This is to prevent infinitely long executions. Defaults to 1e-6.

            Returns:
                defaultdict[DiscreteKey, float]: The new distribution of the exploded dice.
            """

            new_dist = defaultdict[DiscreteKey, float](float)

            for key in dist:
                new_key = base_key + key
                new_key = self._sort_key(new_key)
                new_odds = base_odds * dist.get(key, 0)
                if new_odds < cutoff:
                    new_dist[new_key] = cutoff
                    return new_dist

                if not should_explode(selector, sum(key)):
                    new_dist[new_key] += new_odds
                    continue
                exploded = apply_explode(dist, selector, new_odds, new_key)
                for key in exploded:
                    new_dist[key] += exploded.get(key, 0)

            return new_dist

        for selector in selectors:
            self._dist = apply_explode(self._dist, selector, 1.0, ())

    def apply_ra(self, selectors: list[Selector]) -> None:
        for selector in selectors:
            new_dist = defaultdict[DiscreteKey, float](float)
            for key, probability in self._dist.items():
                # Check if the key matches the selector
                matches = False

                # If the selector is highest or lowest, and at least one element is selected,
                # then it is always true
                if selector.cat in ["h", "l"] and selector.num > 0:
                    matches = True

                # Otherwise, check if at least one value in the key matches
                elif any(self._matches_selector(value, selector) for value in key):
                    matches = True

                if not matches:
                    new_dist[key] += probability
                else:
                    # At this point, the matches, and we just need to add the newly rolled value
                    # to the key, and distribute the probability over all possibilities
                    probability_per_roll = probability / self._sides
                    for roll in range(1, self._sides + 1):
                        new_key = key + (roll,)
                        new_key = self._sort_key(new_key)
                        new_dist[new_key] += probability_per_roll

            self._dist = new_dist

    def apply_rr(self, selectors: list[Selector]) -> None:
        def get_repeated_reroll_dice_probabilities(
            dice: DiscreteKey, sides: int, selector: Selector
        ) -> dict[DiscreteKey, float]:
            """Get the repeated reroll distribution of re-rolling a single key.

            Args:
                dice (DiscreteKey): The key to reroll on.
                sides (int): The number of sides of the dice.
                selector (Selector): The selector of the re-roll.

            Returns:
                dict[DiscreteKey, float]: A distribution containing the keys and their rerolled values. The total probabilities add up to one.
            """

            if len(dice) == 0:
                return {(): 1.0}

            value, *rest = dice

            # The current value does not need to be rerolled
            if not self._matches_selector(value, selector):
                new_dist = defaultdict[DiscreteKey, float](float)
                sub_dist = get_repeated_reroll_dice_probabilities(tuple(rest), sides, selector)
                for sub_key, probability in sub_dist.items():
                    new_key = self._sort_key((value,) + sub_key)
                    new_dist[new_key] += probability
                return new_dist

            # The current value does need to be rerolled
            possible_reroll_values: list[int] = []
            for possible_value in range(1, sides + 1):
                # Get a list of all values that will not be re-rolled, so the probability
                # can be distributed over them.
                if not self._matches_selector(possible_value, selector):
                    possible_reroll_values.append(possible_value)

            if len(possible_reroll_values) == 0:
                raise RollError(f"Selector {str(selector)} could not be re-rolled for {self._count}d{self._sides}!")

            new_dist = defaultdict[DiscreteKey, float](float)
            sub_dist = get_repeated_reroll_dice_probabilities(tuple(rest), sides, selector)
            probability_per_reroll_value = 1.0 / len(possible_reroll_values)
            for reroll_value in possible_reroll_values:
                for sub_key, probability in sub_dist.items():
                    new_key = self._sort_key((reroll_value,) + sub_key)
                    new_dist[new_key] += probability * probability_per_reroll_value
            return new_dist

        for selector in selectors:
            if self._creates_infinite_rr_loop(self._count, self._sides, selector):
                raise RollError(
                    f"Selector {str(selector)} will result in an infinite rr reroll loop for"
                    f" {self._count}d{self._sides}!"
                )

            new_dist = defaultdict[DiscreteKey, float](float)
            for key, probability in self._dist.items():
                sub_dist = get_repeated_reroll_dice_probabilities(key, self._sides, selector)
                for new_key, sub_probability in sub_dist.items():
                    new_dist[new_key] += probability * sub_probability

            self._dist = new_dist
