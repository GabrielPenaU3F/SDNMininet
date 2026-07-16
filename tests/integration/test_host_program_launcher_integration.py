from pathlib import Path

from controllers.base_controller.controller import BaseController
from experiments.experiment import Experiment
from launchers.host_program_launcher import HostProgramLauncher
from topologies.simple_topology import SimpleTopology


class HostProgramIntegrationExperiment(Experiment):

    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def run(self):
        h1 = self.net.get('h1')

        launcher = HostProgramLauncher(self.context)
        launcher.launch(
            h1,
            'tests/integration/scripts/create_file.py'
        ).wait()


class TestHostProgramLauncherIntegration:

    def test_host_program_runs_inside_experiment_root(self, make_experiment):
        experiment = make_experiment(HostProgramIntegrationExperiment)
        experiment.execute()
        assert Path(
                experiment.context.experiment_root
                / 'measurements'
                / 'host_program.txt'
        ).exists()