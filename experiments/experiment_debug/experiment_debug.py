from experiments.experiment import Experiment
from experiments.experiment_debug.debug_controller import DebugController
from hosts.host_apps.minimal_apps import SilentListenerHostApp, DeafSpeakerHostApp
from topologies.simple_topology import SimpleTopology


class ExperimentDebug(Experiment):

    def begin(self):
        speaker = self.network_mgr.host('h1')
        listener = self.network_mgr.host('h2')

        listener.launch_app(
            SilentListenerHostApp,
            self.app_context,
            port=100
        )

        speaker.launch_app(
            DeafSpeakerHostApp,
            self.app_context,
            dst_ip='10.0.0.2',
            port=100
        )

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
