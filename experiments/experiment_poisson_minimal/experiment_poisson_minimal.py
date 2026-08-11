from core.controllers.debug_controller import DebugController
from experiments.experiment import Experiment
from hosts.host_apps.minimal_apps import VerboseSilentListenerHostApp
from hosts.host_apps.udp_arrival_speaker_host_app import PoissonArrivalSpeakerHostApp
from topologies.simple_topology import SimpleTopology


class ExperimentPoissonMinimal(Experiment):

    def begin(self):
        sender, receiver = (self.network_mgr.host('h1'), self.network_mgr.host('h2'))
        rate = 10
        seed = 1

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
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
