import pytest

from config.execution_context import ExecutionContext


@pytest.fixture
def execution_context():
    return ExecutionContext(duration=0.001, seed=42)
