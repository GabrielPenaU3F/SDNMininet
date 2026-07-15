from argparse import Namespace

import pytest

from unittest.mock import Mock

from launchers.experiment_launcher import ExperimentLauncher
from tests.dummies.dummy_experiment import DummyExperiment


@pytest.fixture
def valid_argv(monkeypatch):
    monkeypatch.setattr(
        'sys.argv',
        [
            'run.py',
            'dummy_experiment'
        ]
    )

@pytest.fixture
def launcher():
    dummy_register = {'dummy_experiment': DummyExperiment}
    return ExperimentLauncher(dummy_register)

class TestLoadExperiment:

    def test_load_existing_experiment(self, launcher, execution_context):
        experiment = launcher._load_experiment('dummy_experiment', execution_context)
        assert isinstance(experiment, DummyExperiment)

    def test_validate_rejects_unknown_experiment(self, launcher, capsys):
        args = Namespace(
            experiment='pepe',
            duration=60
        )

        with pytest.raises(SystemExit):
            launcher._validate_args(args)

        output = capsys.readouterr().out
        assert 'Unknown experiment' in output
        assert 'dummy_experiment' in output

    def test_validate_rejects_non_positive_duration(self, launcher, capsys):
        args = Namespace(
            experiment='dummy_experiment',
            duration=0
        )

        with pytest.raises(SystemExit):
            launcher._validate_args(args)

        output = capsys.readouterr().out
        assert 'duration' in output.lower()

    def test_validate_accepts_valid_arguments(self, launcher):
        args = Namespace(experiment='dummy_experiment', duration=60)
        launcher._validate_args(args)

    def test_ensure_root_does_nothing_if_already_root(self, launcher, monkeypatch):
        monkeypatch.setattr('os.geteuid', lambda: 0)

        execvp = Mock()

        monkeypatch.setattr("os.execvp", execvp)
        launcher._ensure_root()

        execvp.assert_not_called()

    def test_ensure_root_relaunches_with_sudo(self, launcher, monkeypatch, valid_argv):
        monkeypatch.setattr("os.geteuid", lambda: 1000)

        monkeypatch.setattr(
            "sys.executable",
            "/home/user/.venv/bin/python"
        )

        execvp = Mock()
        monkeypatch.setattr("os.execvp", execvp)

        launcher._ensure_root()

        expected = [
            "sudo",
            "/home/user/.venv/bin/python",
            "run.py",
            "dummy_experiment"
        ]

        execvp.assert_called_once_with(
            "sudo",
            expected
        )
