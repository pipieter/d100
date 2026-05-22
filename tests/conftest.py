import pytest

import d100


@pytest.fixture(autouse=True, scope="function")
def global_fixture():
    """Seed each individual test with the same seed, so that different runs of the same test are deterministic"""
    d100.seed(42)
    yield
