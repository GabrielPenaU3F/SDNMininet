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

    def test_unknown_experiment_exits(self, capsys):
        with pytest.raises(SystemExit):
            load_experiment('pepe')

        captured = capsys.readouterr()

        assert 'Unknown experiment' in captured.out
        assert 'dummy_experiment' in captured.out

    def test_valid_arguments(self, monkeypatch, valid_argv):
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
                'dummy_experiment',
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
