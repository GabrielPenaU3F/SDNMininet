from pathlib import Path
from unittest.mock import Mock

from launchers.host_program_launcher import HostProgramLauncher


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

    def test_launch_invokes_popen_with_expected_command(self, monkeypatch, tmp_path):
        context = Mock()
        context.experiment_root = tmp_path / 'experiments'
        context.stdout_path = tmp_path / 'stdout'

        context.experiment_root.mkdir()
        context.stdout_path.mkdir()

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
        mn_process_launcher.name = 'h1'

        process = object()
        mn_process_launcher.popen.return_value = process

        result = launcher.launch(
            mn_process_launcher,
            'host_program.py',
            rate=100,
            duration=60
        )

        args, kwargs = mn_process_launcher.popen.call_args

        assert args == (
            [
                '/.venv/bin/python',
                Path('/project/host_program.py'),
                '--rate', '100',
                '--duration', '60'
            ],
        )

        assert kwargs['env'] == {'PYTHONPATH': '/project'}
        assert kwargs['cwd'] == context.experiment_root

        assert kwargs['stdout'].name == str(context.stdout_path / 'h1.out')
        assert kwargs['stderr'].name == str(context.stdout_path / 'h1.err')

        assert result is process