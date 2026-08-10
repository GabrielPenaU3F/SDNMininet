import json
from pathlib import Path

from core.config.environment import Environment
from hosts.host_app import HostApp, HostAppContext


class Host:

    def __init__(self, mn_host):
        self.mn_host = mn_host
        self.process = None
        self.app = None

    #TODO: this should terminate the running process
    def _stop(self):
        pass

    @property
    def name(self):
        return self.mn_host.name

    @property
    def ip(self):
        return self.mn_host.IP()

    def cmd(self, *args, **kwargs):
        return self.mn_host.cmd(*args, **kwargs)

    def popen(self, *args, **kwargs):
        self.process = self.mn_host.popen(*args, **kwargs)
        return self.process

    def launch_app(self, app: HostApp, app_context: HostAppContext, **kwargs):
        if self.app is not None:
            raise RuntimeError(f'Host {self.name} already has an application running')

        command = self._build_app_command(app, **kwargs)

        stdout = open(app_context.stdout_path / f'{self.name}.out', 'w')
        stderr = open(app_context.stdout_path / f'{self.name}.err', 'w')

        self.process = self.popen(
            command,
            env=Environment.get_env_dict(),
            cwd=app_context.experiment_root,
            stdout=stdout,
            stderr=stderr
        )
        self.app = app

        stdout.close()
        stderr.close()


    @staticmethod
    def _build_app_command(app, **kwargs):
        python_path = str(Environment.get_environment().python_path)
        runner_path = str(Environment.get_environment().app_runner_path)

        command = [
            python_path,
            runner_path,
            '--app-module',
            type(app).__module__,
            '--app-class',
            type(app).__name__,
            '--app-kwargs',
            json.dumps(kwargs)
        ]
        return command