from pathlib import Path
from typing import Optional

from config.environment import Environment


class ExperimentConfig:

    def __init__(
        self,
        experiment_name,
        duration=10,
        seed=42,
        sampling_interval=0.1,
        experiment_root=None,
    ):
        self.experiment_name = experiment_name
        self.duration = duration
        self.seed = seed
        self.sampling_interval = sampling_interval

        # Root directory initialization
        self.experiment_root = self._calculate_experiment_root(experiment_root, experiment_name)
        self._initialize_experiment_root_directory()


    @classmethod
    def from_args(cls, args):
        return cls(
            experiment_name=args.experiment,
            duration=args.duration,
            seed=args.seed,
            sampling_interval=args.sampling_interval,
            experiment_root=getattr(args, 'experiment_path', None),
        )

    @staticmethod
    def _calculate_experiment_root(experiment_root: Optional[Path], experiment_name: str) -> Path:
        if experiment_root is None:
            experiment_root = Environment.get_environment().experiments_path

        return Path(experiment_root) / experiment_name


    def _initialize_experiment_root_directory(self):
        self.measurements_path.mkdir(
            parents=True,
            exist_ok=True
        )

    # Properties

    @property
    def controller_config_file(self):
        return (
            Environment.get_environment().temp_path
            / f'{self.experiment_name}_cfg.json'
        )

    @property
    def measurements_path(self):
        return self.experiment_root / 'measurements'
