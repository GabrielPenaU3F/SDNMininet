from pathlib import Path
from unittest.mock import Mock

from config.environment import Environment
from launchers.host_program_launcher import HostProgramLauncher


class TestHostProgramLauncher:

    def test_build_command_args(self):
        launcher = HostProgramLauncher(context=Mock())

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

    def test_launch_invokes_popen_with_expected_command(self, monkeypatch, tmp_path):
        context = Mock()
        context.experiment_root = tmp_path / 'experiments'
        launcher = HostProgramLauncher(context)

        environment = Mock()
        environment.python_path = '/.venv/bin/python'
        environment.project_root = Path('/project')

        monkeypatch.setattr(
            'launchers.host_program_launcher.Environment.get_environment',
            Mock(return_value=environment)
        )

        monkeypatch.setattr(
            'launchers.host_program_launcher.Environment.get_env_dict',
            Mock(return_value={'PYTHONPATH': '/project'})
        )

        mn_process_launcher = Mock()
        process = object()
        mn_process_launcher.popen.return_value = process

        result = launcher.launch(
            mn_process_launcher,
            'host_program.py',
            rate=100,
            duration=60
        )

        mn_process_launcher.popen.assert_called_once_with(
            [
                '/.venv/bin/python',
                Path('/project/host_program.py'),
                '--rate', '100',
                '--duration', '60'
            ],
            env={'PYTHONPATH': '/project'},
            cwd=tmp_path / 'experiments'
        )

        assert result is process