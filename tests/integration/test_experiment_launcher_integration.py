from launchers.experiment_launcher import ExperimentLauncher
from tests.dummies.dummy_experiment import DummyExperiment


class TestExperimentLauncherIntegration:

    def test_can_launch_experiment(self, experiment_config):
        dummy_register = {'dummy_experiment': DummyExperiment}
        launcher = ExperimentLauncher(dummy_register)
        launcher._launch(experiment_config)