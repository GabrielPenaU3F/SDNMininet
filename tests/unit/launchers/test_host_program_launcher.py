from unittest.mock import Mock

from launchers.host_program_launcher import HostProgramLauncher


class TestHostProgramLauncher:

    def test_build_command_args(self):
        launcher = HostProgramLauncher()

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

    def test_launch_invokes_popen_with_expected_command(self, monkeypatch):
        launcher = HostProgramLauncher()

        environment = Mock()
        environment.python_path = '/venv/bin/python'

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
                '/venv/bin/python',
                'host_program.py',
                '--rate', '100',
                '--duration', '60'
            ],
            env={'PYTHONPATH': '/project'}
        )

        assert result is process