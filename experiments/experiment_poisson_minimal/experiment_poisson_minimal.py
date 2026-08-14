from core.controllers.monitor_controller import MonitorController
from experiments.experiment import Experiment
from hosts.host_apps.minimal_apps import VerboseSilentListenerHostApp
from hosts.host_apps.udp_apps.speaker_arrival_apps import PoissonArrivalSpeakerHostApp
from topologies.simple_topology import SimpleTopology


class ExperimentPoissonMinimal(Experiment):

    def _begin(self):
        sender, receiver = (self.network_mgr.host('h1'), self.network_mgr.host('h2'))
        seed = self.config.seed
        rate = 10

        # Receiver
        receiver.launch_app(VerboseSilentListenerHostApp,
                            self.app_context,
                            port=100)

        # Sender
        sender.launch_app(PoissonArrivalSpeakerHostApp,
                          self.app_context,
                          dst_ip=receiver.ip,
                          port=100,
                          rate=rate,
                          seed=seed)

    @property
    def controller_cls(self):
        return MonitorController

    @property
    def topology_cls(self):
        return SimpleTopology
