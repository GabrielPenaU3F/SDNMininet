import os
from pathlib import Path

PYTHON_VENV_PATH = '/home/sskies/SDN/.venv/bin/python'
CONTROLLER_READY_SOCK = 'temp/ryu_ready.sock'

class Environment:

    instance = None

    def __init__(self, project_root=None, experiment_root=None):

        if project_root is None:
            project_root = self._find_project_root()
        self.project_root = Path(project_root)

        if experiment_root is None:
            experiment_root = self.experiments_path
        self.experiment_root = Path(experiment_root)

        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.project_root)
        self.env = env
        self.python_path = PYTHON_VENV_PATH
        self._create_required_directories()

        # Needs the directories created
        self.controller_ready_sock = str(self.project_root / CONTROLLER_READY_SOCK)


    # Properties

    @property
    def topologies_path(self) -> Path:
        return self.project_root / 'topologies'

    @property
    def controllers_path(self) -> Path:
        return self.project_root / 'controllers'

    @property
    def experiments_path(self) -> Path:
        return self.project_root / 'experiments'

    @property
    def temp_path(self) -> Path:
        return self.project_root / 'temp'

    @property
    def _required_directories(self):
        return (
            self.controllers_path,
            self.topologies_path,
            self.experiments_path,
            self.temp_path,
        )

    # Class methods

    @classmethod
    def get_environment(cls):
        if cls.instance is None:
           cls.instance = Environment()
        return cls.instance

    @classmethod
    def get_env_dict(cls):
        return cls.get_environment().env

    @staticmethod
    def _find_project_root():
        current = Path(__file__).resolve().parent

        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent

        raise RuntimeError('Unable to find project root')

    def _create_required_directories(self):
        for directory in self._required_directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _reset_instance(cls):
        cls.instance = None