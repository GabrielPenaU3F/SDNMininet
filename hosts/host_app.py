from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class HostApp(ABC):

    @abstractmethod
    def run(self):
        pass


@dataclass
class HostAppContext:
    experiment_root: Path
    stdout_path: Path
