from argparse import Namespace

import pytest

from config.execution_context import ExecutionContext


@pytest.fixture
def execution_context(tmp_path):
    return ExecutionContext(experiment_name='dummy_experiment',
                            duration=0.001, seed=42, experiment_root=tmp_path)

@pytest.fixture
def context_args(tmp_path):
    return Namespace(experiment='dummy_experiment', duration=0.001, seed=42, experiment_path=tmp_path,
                     sampling_interval=1.0)
