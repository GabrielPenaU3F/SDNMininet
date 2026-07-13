from unittest.mock import Mock

import pytest

from experiments.experiment_1.experiment_1 import Experiment1
from launchers.launch_experiment import load_experiment, validate_args, ensure_root


class TestLoadExperiment:

    def test_load_existing_experiment(self):
        experiment = load_experiment('experiment_1')
        assert isinstance(experiment, Experiment1)

    def test_unknown_experiment_exits(self, capsys):
        with pytest.raises(SystemExit):
            load_experiment('pepe')

        captured = capsys.readouterr()

        assert 'Unknown experiment' in captured.out
        assert 'experiment_1' in captured.out

    def test_valid_arguments(self, monkeypatch):
        monkeypatch.setattr(
            'sys.argv',
            [
                'run.py',
                'experiment_1'
            ]
        )
        validate_args()

    def test_no_arguments_raises_exception(self, monkeypatch):
        monkeypatch.setattr(
            'sys.argv',
            [
                'run.py'
            ]
        )
        with pytest.raises(SystemExit):
            validate_args()

    def test_too_many_arguments_raise_exception(self, monkeypatch):
        monkeypatch.setattr(
            'sys.argv',
            [
                'run.py',
                'experiment_1',
                'another_arg'
            ]
        )
        with pytest.raises(SystemExit):
            validate_args()

    def test_invalid_usage_prints_help(self, monkeypatch, capsys):
        monkeypatch.setattr(
            'sys.argv',
            [
                'run.py'
            ]
        )
        with pytest.raises(SystemExit):
            validate_args()

        output = capsys.readouterr().out
        assert 'Usage' in output
        assert 'Available' in output

    def test_ensure_root_does_nothing_if_already_root(self, monkeypatch):
        monkeypatch.setattr("os.geteuid", lambda: 0)

        execvp = Mock()

        monkeypatch.setattr("os.execvp", execvp)
        ensure_root()

        execvp.assert_not_called()

    def test_ensure_root_relaunches_with_sudo(self, monkeypatch):
        monkeypatch.setattr("os.geteuid", lambda: 1000)

        monkeypatch.setattr(
            "sys.executable",
            "/home/user/.venv/bin/python"
        )

        monkeypatch.setattr(
            "sys.argv",
            [
                "run.py",
                "experiment_1"
            ]
        )

        execvp = Mock()
        monkeypatch.setattr("os.execvp", execvp)

        ensure_root()

        execvp.assert_called_once_with(
            "sudo",
            [
                "sudo",
                "/home/user/.venv/bin/python",
                "run.py",
                "experiment_1"
            ]
        )