import inspect
import socket
import subprocess
import time

from core.config.environment import Environment
from core.config.experiment_config import ExperimentConfig


class ControllerManager:

    def __init__(self, controller_cls, timeout=30):
        self.controller_cls = controller_cls
        self._timeout = timeout
        self._process = None

    def start(self, config: ExperimentConfig):
        self.config = config
        if self._process:
            raise RuntimeError('Controller already running. Terminate before re-launching')
        self._process = self._launch_controller(config)

        try:
            self._wait_until_ready()
        except Exception:
            self.stop()
            raise

    def stop(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None

    def _launch_controller(self, config):
        env = Environment.get_environment()
        ryu_manager = env.ryu_manager_path
        controller_path = self._resolve_controller_path()
        stdout = open(config.stdout_path / 'controller.out', 'w')
        stderr = open(config.stdout_path / 'controller.err', 'w')

        env_dict = Environment.get_env_dict().copy()
        env_dict['EXPERIMENT_CFG'] = str(config.config_file)
        proc = subprocess.Popen(
            [
                ryu_manager,
                controller_path,
            ],
            env=env_dict,
            cwd=config.experiment_root,
            stdout=stdout,
            stderr=stderr
        )

        stdout.close()
        stderr.close()

        return proc

    def _wait_until_ready(self):
        deadline = time.monotonic() + self._timeout
        socket_path = Environment.get_environment().controller_ready_sock

        while True:

            if self._timed_out(deadline):
                raise TimeoutError( f'Controller was not correctly initialized')

            if not self._is_process_alive():
                raise RuntimeError(f'Controller ended unexpectedly with code {self._process.returncode}')

            if self._is_controller_ready(socket_path):
                return

            time.sleep(1)

    def _is_process_alive(self) -> bool:
        return self._process.poll() is None

    @staticmethod
    def _timed_out(deadline):
        return time.monotonic() >= deadline

    @staticmethod
    def _is_controller_ready(socket_path) -> bool:

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(str(socket_path))
            except FileNotFoundError:
                return False

            return sock.recv(1024) == b'READY'

    def _resolve_controller_path(self):
        return inspect.getfile(self.controller_cls)

    @property
    def is_running(self):
        return self._process is not None
