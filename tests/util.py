import random


class FixedRandom(random.Random):
    """Provide fixed values for definitive randomness simulations."""

    def __init__(self, values: list[int]) -> None:
        super().__init__()
        self._values = list(values)

    def randrange(
        self, start: int, stop: int | None = None, step: int = 1
    ) -> int:
        assert stop is None
        assert step == 1
        value = self._values.pop(0)
        assert 1 <= value <= start
        return value - 1
