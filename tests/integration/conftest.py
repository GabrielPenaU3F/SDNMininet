import pytest

from config.environment import Environment
from config.execution_context_factory import ExecutionContextFactory


@pytest.fixture
def make_experiment(context_args, tmp_path):
    def _make(experiment_cls):
        tmp_root = tmp_path

        Environment._reset_instance()
        Environment.instance = Environment(
            project_root=None,
            experiment_root=tmp_root
        )
        context = ExecutionContextFactory().make_context(context_args)
        return experiment_cls(context)
    return _make