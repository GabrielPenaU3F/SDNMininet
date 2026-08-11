import time

from experiments.experiment import Experiment
from experiments.experiment_debug.debug_controller import DebugController
from tests.utilities.dummy_host_apps import WriteFileHostApp
from topologies.simple_topology import SimpleTopology


class HostAppIntegrationExperiment(Experiment):

    def begin(self):
        h1 = self.network_mgr.host('h1')
        h1.launch_app(
            WriteFileHostApp,
            self.app_context
        )

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology


class IntegrationTestExperiment(Experiment):

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology

    def begin(self):
        h1 = self.network_mgr.host('h1')
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
