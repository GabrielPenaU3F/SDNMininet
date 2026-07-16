import pytest

from pathlib import Path

from config.environment import Environment
from config.execution_context import ExecutionContext


class TestExecutionContext:

    def test_uses_given_experiment_root(self, tmp_context, tmp_path):
        assert tmp_context.experiment_root == tmp_path

    def test_default_experiment_root_comes_from_environment(self, monkeypatch, tmp_path):
        fake_env = type('FakeEnvironment', (), {
            'experiments_path': tmp_path
        })()

        monkeypatch.setattr(
            Environment,
            'get_environment',
            lambda: fake_env
        )

        context = ExecutionContext(duration=0.001, seed=42)
        assert context.experiment_root == tmp_path

    def test_initialization_creates_measurements_directory(self, tmp_context, tmp_path):
        assert Path(tmp_context.experiment_root / 'measurements').exists()
        assert Path(tmp_context.experiment_root / 'measurements').is_dir()

    def test_measurements_path_is_inside_experiment_root(self, tmp_path):
        context = ExecutionContext(duration=0.001, seed=42, experiment_root=tmp_path)
        expected = tmp_path / 'measurements'
        assert context.experiment_root / 'measurements' == expected
