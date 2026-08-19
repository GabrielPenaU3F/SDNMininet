
from core.controllers.csv_traffic_stats_controller import CSVTrafficStatsController
from experiments.experiment import Experiment
from hosts.host_apps.minimal_apps import SilentListenerHostApp
from hosts.host_apps.udp_apps.speaker_arrival_apps import PoissonArrivalSpeakerHostApp
from topologies.simple_topology import SimpleTopology

'''

DESCRIPTION

1 source emmit Poisson, traffic, with a fixed rate of 30 packets per second

'''

class Experiment0(Experiment):

    def _begin(self):
        sender, receiver = (self.network_mgr.host('h1'), self.network_mgr.host('h2'))
        seed = self.config.seed
        rate = 30

        # Receiver
        receiver.launch_app(SilentListenerHostApp,
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
        return CSVTrafficStatsController

    @property
    def topology_cls(self):
        return SimpleTopology
