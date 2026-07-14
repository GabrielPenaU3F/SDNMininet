import argparse
import os
import sys

from experiments.experiment_register import EXPERIMENTS


def load_experiment(name):
    return EXPERIMENTS[name]()

def show_available_experiments():
    print('Available experiments:')
    for experiment_name in EXPERIMENTS:
        print(f'    {experiment_name}')


def ensure_root():
    if os.geteuid() != 0:
        print('Retrieving privileges...')
        os.execvp('sudo',
                  [
                      'sudo',
                      sys.executable,
                      *sys.argv
                  ]
                  )


def validate_args(args):
    if args.experiment not in EXPERIMENTS:
        print(f'Unknown experiment: {args.experiment}')
        print()
        show_available_experiments()
        sys.exit(1)

    if args.duration <= 0:
        print('Experiment duration must be positive')
        sys.exit(1)

def parse_args():
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


def main():
    args = parse_args()
    validate_args(args)
    ensure_root()

    print('Launching experiment')

    experiment = load_experiment(args.experiment)
    experiment.execute(duration=args.duration)

    print('Experiment complete')


if __name__ == '__main__':
    main()
