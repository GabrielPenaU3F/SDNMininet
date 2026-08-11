import time

from experiments.experiment_debug.debug_controller import DebugController
from experiments.experiment_debug.experiment_debug import ExperimentDebug
from tests.utilities.dummy_host_apps import WriteFileHostApp
from topologies.simple_topology import SimpleTopology


class HostAppIntegrationExperiment(ExperimentDebug):

    def begin(self):
        h1 = self.network_mgr.host('h1')
        h1.launch_app(
            WriteFileHostApp,
            self.app_context
        )


class IntegrationTestExperiment(ExperimentDebug):

    def begin(self):
        h1 = self.network_mgr.host('h1')
        h1.cmd('ping -c 3 h2')
        time.sleep(2)


class SamplingIntervalExperiment(ExperimentDebug):

    def begin(self):
        time.sleep(0.5)
