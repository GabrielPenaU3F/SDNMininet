import json
from pathlib import Path
from typing import List

from core.config.environment import Environment
from hosts.host import Host
from hosts.host_app import HostApp


class HostAppLauncher:

    def __init__(self, experiment_config):
        self.experiment_config = experiment_config

    def launch(self, host: Host, app_cls, **app_kwargs):
        command = self._build_command(app_cls, **app_kwargs)
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

    @staticmethod
    def _build_command(app_cls, **app_kwargs) -> List[str]:
        python_path = Environment.get_environment().python_path
        runner_path = str(Path(__file__).with_name('host_app_runner.py'))

        command = [
            python_path,
            runner_path,
            '--app-module',
            app_cls.__module__,
            '--app-class',
            app_cls.__name__,
            '--app-kwargs',
            json.dumps(app_kwargs)
        ]
        return command
