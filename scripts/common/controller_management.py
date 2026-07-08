import socket
import subprocess
import time

from mininet.clean import cleanup

from src.environment import Environment

RYU_MGR = "/home/sskies/SDN/.venv/bin/ryu-manager"

def start_controller(controller_path, manager=RYU_MGR, logfile="logs/controller.log"):
    env = Environment.get_env_dict()
    cleanup()
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
                f"El controlador terminó inesperadamente con código {controller.returncode}"
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
        f"El controlador no se inicializó correctamente"
    )