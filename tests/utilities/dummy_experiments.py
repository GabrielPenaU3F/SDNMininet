import time

from experiments.experiment_debug.experiment_debug import ExperimentDebug
from hosts.host_apps.minimal_apps import SilentListenerHostApp
from tests.utilities.dummy_host_apps import WriteFileHostApp, FastDeafSpeakerTestHostApp


class HostAppIntegrationExperiment(ExperimentDebug):

    def _begin(self):
        h1 = self.network_mgr.host('h1')
        h1.launch_app(
            WriteFileHostApp,
            self.app_context
        )


class IntegrationTestExperiment(ExperimentDebug):

    def _begin(self):
        h1 = self.network_mgr.host('h1')
        h1.cmd('ping -c 3 h2')
        time.sleep(2)


class SamplingIntervalExperiment(ExperimentDebug):

    def _begin(self):
        time.sleep(0.5)


class MacLearningIntegrationExperiment(ExperimentDebug):

    def _begin(self):
        h1 = self.network_mgr.host('h1')
        h2 = self.network_mgr.host('h2')

        h2.launch_app(
            SilentListenerHostApp,
            self.app_context,
            port=100
        )

        h1.launch_app(
            FastDeafSpeakerTestHostApp,
            self.app_context,
            dst_ip=h2.ip,
            port=100
        )