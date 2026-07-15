from dataclasses import dataclass
from pathlib import Path

from config.environment import Environment


@dataclass(frozen=True)
class ExecutionContext:

    duration: float
    seed: int
    experiment_root: Path = None

    def __post_init__(self):
        if self.experiment_root is None:
            object.__setattr__(self,'experiment_root', Environment.get_environment().experiments_path)
        self._ensure_directories()

    def _ensure_directories(self):
        (self.experiment_root / 'measurements').mkdir(parents=True, exist_ok=True)
