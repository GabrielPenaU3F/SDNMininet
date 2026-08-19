import numpy as np

from core.controllers.csv_traffic_stats_controller import CSVTrafficStatsController
from experiments.experiment import Experiment
from hosts.host_apps.udp_apps.txrx_arrival_apps import PoissonArrivalTXRXHostApp
from topologies.awad_topology import AwadDDoSTopology

'''

DESCRIPTION

8 sources emmit Poisson, traffic, each one with a
random rate sampled from a U[30, 60] distribution.

'''

class Experiment1(Experiment):

    def _begin(self):
        hosts = [self.network_mgr.host('h1'), self.network_mgr.host('h2'),
                 self.network_mgr.host('h3'), self.network_mgr.host('h4'),
                 self.network_mgr.host('h5'), self.network_mgr.host('h6'),
                 self.network_mgr.host('h7'), self.network_mgr.host('h8')]
        rates = self.rng.uniform(0, 10, 8)
        receivers = set(hosts.copy())

        parent_ss = np.random.SeedSequence(self.config.seed)
        host_seeds = [
            int(np.random.default_rng(ss).integers(2 ** 32))
            for ss in parent_ss.spawn(8)
        ]

        for i in range(8):
            h = hosts[i]
            candidates = [r for r in receivers if r is not h]
            target = self.rng.choice(candidates)
            receivers.remove(target)
            h.launch_app(PoissonArrivalTXRXHostApp,
                         self.app_context,
                         dst_ip=target.ip,
                         port=100,
                         rate=rates[i],
                         seed=host_seeds[i])

    @property
    def controller_cls(self):
        return CSVTrafficStatsController

    @property
    def topology_cls(self):
        return AwadDDoSTopology
