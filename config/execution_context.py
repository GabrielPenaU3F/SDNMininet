from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionContext:
    duration: float
    seed: int