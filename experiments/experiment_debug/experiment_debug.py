from core.config.environment import Environment
from core.controllers.debug_controller import DebugController
from experiments.experiment import Experiment
from hosts.host_apps.debug_apps import SilentListenerHostApp, DeafSpeakerHostApp
from topologies.simple_topology import SimpleTopology


class ExperimentDebug(Experiment):

    def begin(self):
        h1 = self.network_mgr.host('h1')
        h2 = self.network_mgr.host('h2')

        self.app_launcher.launch(
            h2,
            SilentListenerHostApp,
            port=100
        )

        self.app_launcher.launch(
            h1,
            DeafSpeakerHostApp,
            dst_ip='10.0.0.2',
            port=100
        )

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
