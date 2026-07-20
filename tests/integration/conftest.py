import pytest

from config.environment import Environment


@pytest.fixture
def make_experiment(experiment_config, tmp_path):
    def _make(experiment_cls):
        tmp_root = tmp_path

        Environment._reset_instance()
        Environment.instance = Environment(
            project_root=None,
            experiment_root=tmp_root
        )

        return experiment_cls(experiment_config)
    return _make