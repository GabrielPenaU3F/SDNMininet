from dataclasses import dataclass
from pathlib import Path

from config.environment import Environment


@dataclass(frozen=True)
class ExecutionContext:

    experiment_name: str
    duration: float
    seed: int
    experiment_root: Path
    sampling_interval: float = 1.0

@property
def controller_config_file(self):
    return (
        Environment.get_environment().temp_path
        / f'{self.experiment_name}_cfg.json'
    )