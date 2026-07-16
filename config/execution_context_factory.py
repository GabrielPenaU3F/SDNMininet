from pathlib import Path
from typing import Any

from config.environment import Environment
from config.execution_context import ExecutionContext


class ExecutionContextFactory:

    def make_context(self, args):
        experiment_root = self._calculate_experiment_root(args)

        (experiment_root / 'measurements').mkdir(
            parents=True,
            exist_ok=True
        )

        return ExecutionContext(
            duration=args.duration,
            seed=args.seed,
            experiment_root=experiment_root
        )

    @staticmethod
    def _calculate_experiment_root(args) -> Any:
        if args.experiment_path is not None:
            base_path = args.experiment_path
        else:
             base_path = Environment.get_environment().experiments_path

        return Path(base_path / args.name)