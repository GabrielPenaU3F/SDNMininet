from argparse import Namespace
from pathlib import Path

import pytest

from config.execution_context import ExecutionContext
from config.execution_context_factory import ExecutionContextFactory


@pytest.fixture
def factory():
    return ExecutionContextFactory()


class TestExecutionContext:

    def test_uses_given_experiment_root(self, execution_context, tmp_path):
        assert execution_context.experiment_root == tmp_path

    def test_measurements_path_is_inside_experiment_root(self, tmp_path):
        context = ExecutionContext(duration=0.001, seed=42, experiment_root=tmp_path)
        expected = tmp_path / 'measurements'
        assert context.experiment_root / 'measurements' == expected


class TestExecutionContextFactory:

    def test_passes_options_to_context(self, factory, context_args):
        context = factory.make_context(context_args)
        assert context.duration == context_args.duration
        assert context.seed == context_args.seed
        assert context.experiment_root == context_args.experiment_path / context_args.name

    def test_context_root_is_inside_experiments_directory(self, factory, context_args, tmp_path):
        context = factory.make_context(context_args)
        assert context.experiment_root == tmp_path / 'dummy_experiment'

    def test_creates_experiment_directory(self, factory, context_args, tmp_path):
        assert not (tmp_path / 'dummy_experiment').exists()
        factory.make_context(context_args)
        assert (tmp_path / 'dummy_experiment').exists()

    def test_creates_measurements_directory(self, factory, context_args, tmp_path):
        assert not (tmp_path / 'dummy_experiment' / 'measurements').exists()
        factory.make_context(context_args)
        assert (tmp_path / 'dummy_experiment' / 'measurements').exists()
