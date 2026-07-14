from argparse import Namespace

import pytest

from unittest.mock import Mock

from launchers.launch_experiment import load_experiment, validate_args, ensure_root
from tests.dummies.dummy_experiment import DummyExperiment


@pytest.fixture(autouse=True)
def dummy_registry(monkeypatch):
    import launchers.launch_experiment as launcher
    monkeypatch.setattr(
        launcher,
        "EXPERIMENTS",
        {
            "dummy_experiment": DummyExperiment
        }
    )
    yield

@pytest.fixture
def valid_argv(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "run.py",
            "dummy_experiment"
        ]
    )

class TestLoadExperiment:

    def test_load_existing_experiment(self):
        experiment = load_experiment('dummy_experiment')
        assert isinstance(experiment, DummyExperiment)

    def test_validate_rejects_unknown_experiment(self, capsys):
        args = Namespace(
            experiment='pepe',
            duration=60
        )

        with pytest.raises(SystemExit):
            validate_args(args)

        output = capsys.readouterr().out
        assert 'Unknown experiment' in output
        assert 'dummy_experiment' in output

    def test_validate_rejects_non_positive_duration(self, capsys):
        args = Namespace(
            experiment='dummy_experiment',
            duration=0
        )

        with pytest.raises(SystemExit):
            validate_args(args)

        output = capsys.readouterr().out
        assert 'duration' in output.lower()

    def test_validate_accepts_valid_arguments(self):
        args = Namespace(experiment='dummy_experiment', duration=60)
        validate_args(args)

    def test_ensure_root_does_nothing_if_already_root(self, monkeypatch):
        monkeypatch.setattr('os.geteuid', lambda: 0)

        execvp = Mock()

        monkeypatch.setattr("os.execvp", execvp)
        ensure_root()

        execvp.assert_not_called()

    def test_ensure_root_relaunches_with_sudo(self, monkeypatch, valid_argv):
        monkeypatch.setattr("os.geteuid", lambda: 1000)

        monkeypatch.setattr(
            "sys.executable",
            "/home/user/.venv/bin/python"
        )

        execvp = Mock()
        monkeypatch.setattr("os.execvp", execvp)

        ensure_root()

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
