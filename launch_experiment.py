from core.experiment_launcher import ExperimentLauncher
from experiments.registry import EXPERIMENTS


def main():
    ExperimentLauncher(EXPERIMENTS).launch()


if __name__ == '__main__':
    main()
