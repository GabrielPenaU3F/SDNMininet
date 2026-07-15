import argparse
import os
import sys


class ExperimentLauncher:

    def __init__(self, experiments):
        self._experiments = experiments

    def launch(self, argv=None):
        args = self._parse_args(argv)
        self._validate_args(args)
        self._ensure_root()

        print('Launching experiment')

        experiment = self._load_experiment(args.experiment)
        experiment.execute(duration=args.duration)

        print('Experiment complete')

    def _load_experiment(self, name):
        return self._experiments[name]()

    def _show_available_experiments(self):
        print('Available experiments:')
        for experiment_name in self._experiments:
            print(f'{experiment_name}')

    def _ensure_root(self):
        if os.geteuid() != 0:
            print('Retrieving privileges...')
            os.execvp('sudo', ['sudo', sys.executable, *sys.argv])

    def _validate_args(self, args):
        if args.experiment not in self._experiments.keys():
            print(f'Unknown experiment: {args.experiment}')
            print()
            self._show_available_experiments()
            sys.exit(1)

        if args.duration <= 0:
            print('Experiment duration must be positive')
            sys.exit(1)

    def _parse_args(self, argv=None):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            'experiment',
            help='Experiment to execute'
        )

        parser.add_argument(
            '--duration',
            type=float,
            required=True,
            help='Experiment duration in seconds'
        )

        return parser.parse_args()
