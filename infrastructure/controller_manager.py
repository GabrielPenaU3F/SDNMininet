import socket
import subprocess
import time

from config.environment import Environment


class ControllerManager:

    def __init__(self, controller_cls, experiment_root, timeout=30):
        self.controller_cls = controller_cls
        self.experiment_root = experiment_root
        self._timeout = timeout
        self._process = None

    def start(self):
        if self._process:
            raise RuntimeError('Controller already running. Terminate before re-launching')
        self._process = self._launch_controller()
        self._wait_until_ready()

    def stop(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None

    def _launch_controller(self):
        env = Environment.get_environment()
        ryu_manager = env.ryu_manager_path
        controller_path = self._resolve_controller_path()
        return subprocess.Popen(
            [
                ryu_manager,
                controller_path
            ], env=env.get_env_dict(), cwd=self.experiment_root
        )

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

    def _timed_out(self, deadline):
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
        return self.controller_cls.__module__

    @property
    def is_running(self):
        return self._process is not None
