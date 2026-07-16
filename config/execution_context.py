from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionContext:

    duration: float
    seed: int
    experiment_root: Path

