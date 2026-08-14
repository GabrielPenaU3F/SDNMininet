import json
from typing import Type

from core.config.environment import Environment
from hosts.host_apps.host_app import HostApp, HostAppContext


class Host:

    def __init__(self, mn_host):
        self.mn_host = mn_host
        self.process = None
        self.app = None

    def _stop(self):
        if self.process is not None:
            self.process.terminate()
            self.wait()
            self._clear()

    @property
    def name(self):
        return self.mn_host.name

    @property
    def process_running(self):
        return self.process is not None and self.process.poll() is None

    @property
    def ip(self):
        return self.mn_host.IP()

    @property
    def mac(self):
        return self.mn_host.MAC()

    def cmd(self, *args, **kwargs):
        return self.mn_host.cmd(*args, **kwargs)

    def popen(self, *args, **kwargs):
        return self.mn_host.popen(*args, **kwargs)

    def wait(self):
        if self.process is not None:
            return self.process.wait()
        return None

    def launch_app(self, app_cls: Type[type(HostApp)], app_context: HostAppContext, **kwargs):
        if self.process_running:
            raise RuntimeError(f'Host {self.name} already has an application running')

        command = self._build_app_command(app_cls, **kwargs)

        stdout = open(app_context.stdout_path / f'{self.name}.out', 'w')
        stderr = open(app_context.stdout_path / f'{self.name}.err', 'w')

        self.process = self.popen(
            command,
            env=Environment.get_env_dict(),
            cwd=app_context.experiment_root,
            stdout=stdout,
            stderr=stderr
        )
        self.app = app_cls(**kwargs)

        stdout.close()
        stderr.close()

    @staticmethod
    def _build_app_command(app_cls, **kwargs):
        python_path = str(Environment.get_environment().python_path)
        runner_path = str(Environment.get_environment().app_runner_path)

        command = [
            python_path,
            runner_path,
            '--app-module',
            app_cls.__module__,
            '--app-class',
            app_cls.__name__,
            '--app-kwargs',
            json.dumps(kwargs)
        ]
        return command

    def _clear(self):
        self.process = None
        self.app = None
