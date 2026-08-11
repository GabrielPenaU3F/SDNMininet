from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class HostApp(ABC):

    def __init__(self):
        self._clean_resources()

    @abstractmethod
    def run(self):
        pass

    @property
    def logfile(self):
        return Path('logs/logfile.log')

    def _clean_resources(self):
        self.logfile.unlink(missing_ok=True)


@dataclass
class HostAppContext:
    experiment_root: Path
    stdout_path: Path
