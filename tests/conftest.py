from argparse import Namespace

import pytest

from config.experiment_config import ExperimentConfig


@pytest.fixture
def experiment_config(args_namespace):
    return ExperimentConfig.from_args(args_namespace)

@pytest.fixture
def args_namespace(tmp_path):
    return Namespace(experiment='dummy_experiment', duration=0.001, seed=42, experiment_path=tmp_path,
                     sampling_interval=1.0)
