from experiments.experiment_register import EXPERIMENTS
from core.launchers import ExperimentLauncher


def main():
    ExperimentLauncher(EXPERIMENTS).launch()


if __name__ == '__main__':
    main()
