import pytest

from config.environment import Environment
from config.execution_context import ExecutionContext


@pytest.fixture
def execution_context():
    return ExecutionContext(duration=0.001, seed=42)

@pytest.fixture
def tmp_context(tmp_path):
    return ExecutionContext(duration=0.001, seed=42, experiment_root=tmp_path)

@pytest.fixture
def make_experiment(tmp_context, tmp_path):
    def _make(experiment_cls):
        tmp_root = tmp_path

        Environment._reset_instance()
        Environment.instance = Environment(
            project_root=None,
            experiment_root=tmp_root
        )

        return experiment_cls(tmp_context)
    return _make