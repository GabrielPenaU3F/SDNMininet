from typing import List

from core.config.environment import Environment
from hosts.host import Host


class HostProgramLauncher:

    def __init__(self, experiment_config):
        self.experiment_config = experiment_config

    def launch(self, host: Host, script_path: str, **kwargs):
        command = self._build_command(script_path, **kwargs)
        stdout = open(self.experiment_config.stdout_path / f'{host.name}.out', 'w')
        stderr = open(self.experiment_config.stdout_path / f'{host.name}.err', 'w')

        # This process is also stored in the host
        proc = host.popen(
            command,
            env=Environment.get_env_dict(),
            cwd=self.experiment_config.experiment_root,
            stdout=stdout,
            stderr=stderr
        )

        stdout.close()
        stderr.close()
        return proc

    def _build_command(self, script_path: str, **kwargs) -> List[str]:
        python_path = Environment.get_environment().python_path
        script_path = Environment.get_environment().project_root / script_path
        args = self._build_command_args(**kwargs)
        command = [
            python_path,
            script_path,
            *args
        ]
        return command

    @staticmethod
    def _build_command_args(**kwargs):
        args = []
        for key, value in kwargs.items():
            args.append(f'--{key}')
            args.append(str(value))
        return args
