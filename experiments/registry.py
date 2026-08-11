from experiments.experiment_1.experiment_1 import Experiment1
from experiments.experiment_debug.experiment_debug import ExperimentDebug
from experiments.experiment_poisson_minimal.experiment_poisson_minimal import ExperimentPoissonMinimal

EXPERIMENTS = {
    'experiment_debug': ExperimentDebug,
    'experiment_1': Experiment1,
    'experiment_poisson_minimal': ExperimentPoissonMinimal,
}