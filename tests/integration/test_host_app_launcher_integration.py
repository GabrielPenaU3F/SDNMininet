from pathlib import Path

from core.controllers.base_controller import BaseController
from experiments.experiment import Experiment
from tests.utilities.dummy_host_apps import WriteFileHostApp
from topologies.simple_topology import SimpleTopology


class HostAppIntegrationExperiment(Experiment):

    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def begin(self):
        app = WriteFileHostApp()
        h1 = self.network_mgr.host('h1')
        h1.launch_app(
            app,
            self.app_context
        )


class TestHostAppLauncherIntegration:

    def test_host_app_runs_inside_experiment_root(self, make_experiment):
        experiment = make_experiment(HostAppIntegrationExperiment)
        experiment.execute()

        assert Path(
            experiment.config.experiment_root
            / 'measurements'
            / 'host_program.txt'
        ).exists()