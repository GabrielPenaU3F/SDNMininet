import os
from pathlib import Path

PYTHON_VENV_PATH = '/home/sskies/SDN/.venv/bin/python'

class Environment:

    instance = None

    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        self.env = env

        self.python_path = PYTHON_VENV_PATH

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