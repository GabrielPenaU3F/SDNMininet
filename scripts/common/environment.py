import os
from pathlib import Path


class Environment:

    instance = None

    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        self.env = env

    @classmethod
    def get_environment(cls):
        if cls.instance is None:
           cls.instance = Environment()
        return cls.instance.env