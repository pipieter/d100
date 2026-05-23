import abc
from collections.abc import Sequence
from typing import Callable, Iterable

from .ast.operators import Operator as Operator, Selector as Selector
from .errors import RollError as RollError

class Distribution:
    def __init__(self, values: dict[int, float] | None = None) -> None: ...
    def keys(self) -> Iterable[int]:
        """Get the possible dice sums of the distribution.

        Returns:
            Iterable[int]: The possible dice sums of the distribution sorted from lowest to highest.
        """
    def values(self) -> Iterable[float]:
        """Get all stored probability values of the distribution.

        Returns:
            Iterable[float]: The possible probability values of the distribution, in no particular order.
        """
    def get(self, key: int) -> float:
        """Get the probability of a single key.

        Args:
            key (int): The key to retrieve.

        Returns:
            float: The stored probability of the key, or zero if the key is not present.
        """
    def get_at_least(self, key: int) -> float:
        """Get the probability of getting at least the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at least the key, inclusive of the key.
        """
    def get_at_most(self, key: int) -> float:
        """Get the probability of getting at most the key.

        Args:
            key (int): The minimum key to retrieve.

        Returns:
            float: The probability of getting at most the key, inclusive of the key.
        """
    def min(self) -> int:
        """Get the minimum key in the distribution.

        Returns:
            int: The lowest key in the distribution.
        """
    def max(self) -> int:
        """Get the maximum key in the distribution.

        Returns:
            int: The highest key in the distribution.
        """
    def mean(self, key_mapping: Callable[[int], int] | None = None) -> float:
        """Get the mean value of the distribution.

        Args:
            mapping (Optional[Callable[[int], int]], optional): An optional function to perform on the keys of the distribution. Defaults to None.

        Returns:
            float: The mean of the distribution.
        """
    def stdev(self) -> float:
        """Get the standard deviation of the distribution.

        Returns:
            float: The standard deviation of the distribution.
        """
    def __add__(self, other: Distribution) -> Distribution:
        """Adds two distributions together, e.g. 1d20 + 1d4.

        Args:
            other (Distribution): The other distribution to add.

        Returns:
            Distribution: The sum of the two distributions.
        """
    def __sub__(self, other: Distribution) -> Distribution:
        """Subtract two distributions from each other, e.g. 1d20 - 1d4.

        Args:
            other (Distribution): The other distribution to subtract.

        Returns:
            Distribution: The difference of the two distributions.
        """
    def __mul__(self, other: Distribution) -> Distribution:
        """Multiply two distributions together, e.g. 1d20 * 1d4.

        Args:
            other (Distribution): The other distribution to multiply.

        Returns:
            Distribution: The product of the two distributions.
        """
    def __floordiv__(self, other: Distribution) -> Distribution:
        """Divide two distributions from each other, e.g. 1d20 / 1d4. Note that this is the floor
        division, and not the true division, as distribution keys need to be integers.

        Args:
            other (Distribution): The divisor of the division.

        Raises:
            ZeroDivisionError: When one of the possible keys in the divisor is zero.

        Returns:
            Distribution: The division of the two distributions.
        """
    def __mod__(self, other: Distribution) -> Distribution:
        """Use the modulo operator on two distributions, e.g. 1d20 % 1d8.

        Args:
            other (Distribution): The other distribution for the modulo operator.

        Returns:
            Distribution: The resulting modulo operator.
        """
    def __lt__(self, other: Distribution) -> Distribution:
        """Compare two distributions using the less than operator, e.g. 1d6 < 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting less than comparison.
        """
    def __le__(self, other: Distribution) -> Distribution:
        """Compare two distributions using the less than or equal operator, e.g. 1d6 <= 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting less than or equal comparison.
        """
    def __gt__(self, other: Distribution) -> Distribution:
        """Compare two distributions using the greater than operator, e.g. 1d6 > 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting greater than comparison.
        """
    def __ge__(self, other: Distribution) -> Distribution:
        """Compare two distributions using the greater or equal than operator, e.g. 1d6 >= 1d8.

        Args:
            other (Distribution): The other distribution in the comparison.

        Returns:
            Distribution: The resulting greater or equal than comparison.
        """
    def equals(self, other: Distribution) -> Distribution:
        """Compare two distributions using the equality operator, e.g. 1d6 == 1d8.

        Args:
            other (Distribution): The other distribution in the comparison

        Returns:
            Distribution: The resulting equality comparison.
        """
    def not_equals(self, other: Distribution) -> Distribution:
        """Compare two distributions using the inequality operator, e.g. 1d6 != 1d8.

        Args:
            other (Distribution): The other distribution in the comparison

        Returns:
            Distribution: The resulting inequality comparison.
        """
    def __neg__(self) -> Distribution:
        """Negate the values of a distribution.

        Returns:
            Distribution: The distribution with the signs of all of its keys reversed.
        """
    def advantage(self, count: int = 2) -> Distribution:
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
    def disadvantage(self, count: int = 2) -> Distribution:
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
    def __copy__(self) -> Distribution:
        """Create a copy of the distribution. All values of the other distribution
        are deep-copied.

        Returns:
            Distribution: A copy of the distribution.
        """
    def __deepcopy__(self) -> Distribution:
        """Creates a deep copy of the distribution.

        Returns:
            Distribution: A deep copy of the distribution.
        """

class AbstractDistributionBuilder(abc.ABC, metaclass=abc.ABCMeta):
    """An abstract class used to build distributions."""

    @abc.abstractmethod
    def distribution(self) -> Distribution:
        """Build the distribution based on the builder.

        Returns:
            Distribution: The distribution object matching the current state of the distribution.
        """
    def apply_operation(self, op: Operator) -> None:
        """Apply a valid operator to the current distribution. This internally  changes the
        state of the builder

        Args:
            op (Operator): The operator to be applied.

        Raises:
            RollError: When the operation in question is unknown or not supported.
        """
    @abc.abstractmethod
    def apply_mi(self, selectors: list[Selector]) -> None:
        """Apply the minimum operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `mi` operator.
        """
    @abc.abstractmethod
    def apply_ma(self, selectors: list[Selector]) -> None:
        """Apply the maximum operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ma` operator.
        """
    @abc.abstractmethod
    def apply_ro(self, selectors: list[Selector]) -> None:
        """Apply the re-roll once operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ro` operator.
        """
    @abc.abstractmethod
    def apply_e(self, selectors: list[Selector]) -> None:
        """Apply the explode operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `e` operator.
        """
    @abc.abstractmethod
    def apply_k(self, selectors: list[Selector]) -> None:
        """Apply the keep operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `k` operator.
        """
    @abc.abstractmethod
    def apply_p(self, selectors: list[Selector]) -> None:
        """Apply the drop operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `p` operator.
        """
    @abc.abstractmethod
    def apply_ra(self, selectors: list[Selector]) -> None:
        """Apply the reroll and add operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `ra` operator.
        """
    @abc.abstractmethod
    def apply_rr(self, selectors: list[Selector]) -> None:
        """Apply the repeated reroll operator to the builder.

        Args:
            selectors (list[Selector]): A list of valid selectors matching the `rr` operator.
        """

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

    def __init__(self, count: int, sides: int, operations: Sequence[Operator]) -> None:
        """Create a convolution distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[Operator]): A list of operators to be applied to the expression.
        """
    def distribution(self) -> Distribution: ...
    @staticmethod
    def supports_operation(operation: Operator) -> bool:
        """Checks if the ConvolutionDistributionBuilder supports an operation.

        Args:
            operation (Operator): The operation to be checked.

        Returns:
            bool: Whether the operation is supported.
        """
    def apply_mi(self, selectors: list[Selector]) -> None: ...
    def apply_ma(self, selectors: list[Selector]) -> None: ...
    def apply_k(self, selectors: list[Selector]) -> None: ...
    def apply_p(self, selectors: list[Selector]) -> None: ...
    def apply_ro(self, selectors: list[Selector]) -> None: ...
    def apply_e(self, selectors: list[Selector]) -> None: ...
    def apply_ra(self, selectors: list[Selector]) -> None: ...
    def apply_rr(self, selectors: list[Selector]) -> None: ...

DiscreteKey = tuple[int, ...]

class DiscreteDistributionBuilder(AbstractDistributionBuilder):
    def __init__(self, count: int, sides: int, operations: Sequence[Operator]) -> None:
        """Create a discrete distribution builder.

        Args:
            count (int): The number of dice in the expression.
            sides (int): The sides of the dice in the expression.
            operations (list[Operator]): A list of operators to be applied to the expression.
        """
    def distribution(self) -> Distribution: ...
    def apply_mi(self, selectors: list[Selector]) -> None: ...
    def apply_ma(self, selectors: list[Selector]) -> None: ...
    def apply_k(self, selectors: list[Selector]) -> None: ...
    def apply_p(self, selectors: list[Selector]) -> None: ...
    def apply_ro(self, selectors: list[Selector]) -> None: ...
    def apply_e(self, selectors: list[Selector]) -> None: ...
    def apply_ra(self, selectors: list[Selector]) -> None: ...
    def apply_rr(self, selectors: list[Selector]) -> None: ...
