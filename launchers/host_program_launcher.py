from typing import List

from config.environment import Environment

class HostProgramLauncher:

    def __init__(self, experiment_config):
        self.experiment_config = experiment_config
        self.processes = []

    def launch(self, mn_host, script_path: str, **kwargs):
        command = self._build_command(script_path, **kwargs)
        stdout = open(self.experiment_config.stdout_path / f'{mn_host.name}.out', 'w')
        stderr = open(self.experiment_config.stdout_path / f'{mn_host.name}.err', 'w')

        proc = mn_host.popen(
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
