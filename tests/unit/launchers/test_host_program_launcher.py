import pytest

from pathlib import Path
from unittest.mock import Mock

from core.launchers.host_program_launcher import HostProgramLauncher


@pytest.fixture
def example_program_launcher(tmp_path, monkeypatch):
    config = Mock()
    config.experiment_root = tmp_path / 'experiments'
    config.stdout_path = tmp_path / 'stdout'

    config.experiment_root.mkdir()
    config.stdout_path.mkdir()

    launcher = HostProgramLauncher(config)

    environment = Mock()
    environment.python_path = '/.venv/bin/python'
    environment.project_root = Path('/project')

    monkeypatch.setattr(
        'core.launchers.host_program_launcher.Environment.get_environment',
        Mock(return_value=environment)
    )

    monkeypatch.setattr(
        'core.launchers.host_program_launcher.Environment.get_env_dict',
        Mock(return_value={'PYTHONPATH': '/project'})
    )

    return launcher

@pytest.fixture
def dummy_mn_host():
    mn_host = Mock()
    mn_host.name = 'h1'
    process = object()
    mn_host.popen.return_value = process
    return mn_host


class TestHostProgramLauncher:

    def test_build_command_args(self):
        launcher = HostProgramLauncher(experiment_config=Mock())

        args = launcher._build_command_args(
            rate=100,
            destination='10.0.0.2',
            duration=60
        )

        assert args == [
            '--rate', '100',
            '--destination', '10.0.0.2',
            '--duration', '60'
        ]

    # TODO: reimplement so this test passes
    # def test_launch_registers_host_process(self, example_program_launcher, dummy_mn_host):
    #     assert len(example_program_launcher.processes) == 1
    #
    #     host_process = example_program_launcher.processes[0]
    #
    #     assert host_process.name == 'h1'
    #     assert host_process.host is dummy_mn_host
    #     assert host_process.process is dummy_mn_host.popen()

    def test_launch_invokes_popen_with_expected_command(self, example_program_launcher, dummy_mn_host):
        result = example_program_launcher.launch(
            dummy_mn_host,
            'host_program.py',
            rate=100,
            duration=60
        )

        args, kwargs = dummy_mn_host.popen.call_args

        assert args == (
            [
                '/.venv/bin/python',
                Path('/project/host_program.py'),
                '--rate', '100',
                '--duration', '60'
            ],
        )

        assert kwargs['env'] == {'PYTHONPATH': '/project'}
        assert kwargs['cwd'] == example_program_launcher.experiment_config.experiment_root

        assert kwargs['stdout'].name == str(example_program_launcher.experiment_config.stdout_path / 'h1.out')
        assert kwargs['stderr'].name == str(example_program_launcher.experiment_config.stdout_path / 'h1.err')
