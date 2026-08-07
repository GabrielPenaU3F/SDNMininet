import pytest

from core.config.experiment_config import ExperimentConfig


@pytest.fixture
def make_experiment(tmp_path):
    def _make(experiment_cls, name='dummy_experiment', duration=0.001, sampling_interval=1,
              experiment_root=tmp_path):

        config = ExperimentConfig(name,
                                  duration=duration,
                                  sampling_interval=sampling_interval,
                                  experiment_root=experiment_root)
        return experiment_cls(config)
    return _make