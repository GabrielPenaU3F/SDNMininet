from experiments.experiment_register import EXPERIMENTS
from launchers.experiment_launcher import ExperimentLauncher


def main():
    ExperimentLauncher(EXPERIMENTS).launch()


if __name__ == '__main__':
    main()
