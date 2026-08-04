import time
from pathlib import Path

from controllers.debug_controller import DebugController
from experiments.experiment import Experiment
from topologies.simple_topology import SimpleTopology


class IntegrationTestExperiment(Experiment):

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology

    def begin(self):
        h1 = self.net.get('h1')
        h1.cmd('ping -c 3 h2')
        time.sleep(2)


class SamplingIntervalExperiment(Experiment):

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology

    def begin(self):
        time.sleep(0.5)


class TestExperimentIntegration:

    def test_experiment_deploys_real_infrastructure(self, make_experiment, tmp_path):
        experiment = make_experiment(IntegrationTestExperiment)
        experiment.execute()
        file = Path(tmp_path / 'dummy_experiment' / 'measurements' / 'test_file')

        assert file.exists()

        with open(str(file), 'r') as f:
            line = f.readline()
        assert line.rstrip() == 'Debugging...'

    def test_controller_receives_sampling_interval(self, make_experiment, tmp_path):
        experiment = make_experiment(
            SamplingIntervalExperiment,
            sampling_interval=0.05,
            duration=0.5,
        )

        experiment.execute()

        file = tmp_path / 'dummy_experiment' / 'measurements' / 'test_file'
        with open(str(file), 'r') as f:
            line = f.readline()
        assert line.rstrip() == 'SI=0.05'
