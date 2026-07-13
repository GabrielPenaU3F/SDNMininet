import socket
import subprocess
import time

from mininet.clean import cleanup

from src.config.environment import Environment

RYU_MGR = "/home/sskies/SDN/.venv/bin/ryu-manager"


def _cls_to_path(controller_cls):
    return controller_cls.__module__


def start_controller(controller_cls, manager=RYU_MGR, logfile="logs/controller.log"):
    controller_path = _cls_to_path(controller_cls)
    env = Environment.get_env_dict()
    controller = subprocess.Popen(
        [
            manager,
            controller_path
        ], env=env
    )
    _wait_until_controller_is_ready(controller)
    return controller

def stop_controller(controller):
    controller.terminate()
    controller.wait()

def _wait_until_controller_is_ready(controller, timeout=30):
    deadline = time.time() + timeout

    while time.time() < deadline:

        if controller.poll() is not None:
            raise RuntimeError(
                f'Controller ended unexpectedly with code {controller.returncode}'
            )

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(Environment.get_environment().controller_ready_sock)
            except FileNotFoundError: # if the socket was not found
                time.sleep(1)
                continue
            data = sock.recv(1024)
            if data == b'READY':
                return # only in this case we are done
            time.sleep(1) # if the socket exists but does not signal ready, go on

    raise TimeoutError(
        f'Controller was not correctly initialized'
    )