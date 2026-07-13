import os
import sys

from experiments.experiment_register import EXPERIMENTS


def load_experiment(name):

    try:
        return EXPERIMENTS[name]()

    except KeyError:
        print(f'Unknown experiment: {name}')
        print()
        show_available_experiments()
        sys.exit(1)


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


def validate_args():
    if len(sys.argv) != 2:
        print('Usage:')
        print('    python -m launchers.run <experiment>')
        print()
        show_available_experiments()
        sys.exit(1)


def main():

    validate_args()
    ensure_root()
    print('Launching experiment')

    experiment = load_experiment(sys.argv[1])
    experiment.execute()


if __name__ == '__main__':
    main()
