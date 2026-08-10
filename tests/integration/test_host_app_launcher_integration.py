from pathlib import Path

from core.controllers.base_controller import BaseController
from core.launchers.host_app_launcher import HostAppLauncher
from experiments.experiment import Experiment
from tests.utilities.host_apps import WriteFileTestApp
from topologies.simple_topology import SimpleTopology


class HostAppIntegrationExperiment(Experiment):

    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def begin(self):
        h1 = self.network_mgr.host('h1')

        launcher = HostAppLauncher(self.config)

        launcher.launch(
            h1,
            WriteFileTestApp
        ).wait()


class TestHostAppLauncherIntegration:

    def test_host_app_runs_inside_experiment_root(self, make_experiment):
        experiment = make_experiment(HostAppIntegrationExperiment)
        experiment.execute()
        assert Path(
                experiment.config.experiment_root
                / 'measurements'
                / 'host_program.txt'
        ).exists()
