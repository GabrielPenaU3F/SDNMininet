import os
from pathlib import Path

PYTHON_VENV_PATH = '/home/sskies/SDN/.venv/bin/python'
CONTROLLER_READY_SOCK = 'temp/ryu_ready.sock'

class Environment:

    instance = None

    def __init__(self):
        self.project_root = self._find_project_root()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        self.env = env
        self.python_path = PYTHON_VENV_PATH
        self.controller_ready_sock = str(self.project_root / CONTROLLER_READY_SOCK)

    @classmethod
    def get_environment(cls):
        if cls.instance is None:
           cls.instance = Environment()
        return cls.instance

    @classmethod
    def get_env_dict(cls):
        if cls.instance is None:
           cls.instance = Environment()
        return cls.instance.env

    @staticmethod
    def _find_project_root():
        current = Path(__file__).resolve().parent

        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        raise RuntimeError("No se pudo encontrar la raíz del proyecto")
