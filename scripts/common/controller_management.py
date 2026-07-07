import socket
import subprocess
import time

from mininet.clean import cleanup

from scripts.common.environment import Environment

RYU_MGR = "/home/sskies/SDN/.venv/bin/ryu-manager"

def start_controller(controller_path, manager=RYU_MGR,
                     port=6633, logfile="logs/controller.log"):
    env = Environment.get_environment()
    cleanup()
    controller = subprocess.Popen(
        [
            manager,
            controller_path
        ], env=env
    )
    _wait_until_controller_is_ready(controller, port=port)
    return controller

def stop_controller(controller):
    controller.terminate()
    controller.wait()

def _wait_until_controller_is_ready(controller, host="127.0.0.1", port=6633, timeout=10):
    deadline = time.time() + timeout

    while time.time() < deadline:

        if controller.poll() is not None:
            raise RuntimeError(
                f"El controlador terminó inesperadamente con código {controller.returncode}"
            )

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)

            try:
                sock.connect((host, port))
                return
            except (ConnectionRefusedError, OSError):
                time.sleep(0.1)

    raise TimeoutError(
        f"El controlador no comenzó a escuchar en {host}:{port}"
    )