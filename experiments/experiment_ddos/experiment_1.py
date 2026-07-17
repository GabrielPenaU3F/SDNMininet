import numpy as np

from controllers.base_controller.controller import BaseController
from experiments.experiment import Experiment
from topologies.awad_topology import AwadDDoSTopology

'''

DESCRIPTION

Base traffic:
8 sources emmit Poisson, traffic, each one with a
random rate sampled from a U[30, 60] distribution.

'''

class Experiment1(Experiment):

    def run(self):
        hosts = [self.net['h1'], self.net['h2'], self.net['h3'], self.net['h4'],
                 self.net['h5'], self.net['h6'], self.net['h7'], self.net['h8']]
        rates = self.rng.uniform(30, 60, 8)
        receivers = set(hosts.copy())

        for i in range(8):
            h = hosts[i]
            script = '/experiments/shared_host_programs/poisson_udp_host_program.py'
            current_receiver_set = receivers - {h}
            target = self.rng.choice(list(current_receiver_set))
            receivers.remove(target)
            self.program_launcher.launch(h, script_path=script,
                                         dst_ip=target.IP(), port='100', rate=rates[i])


    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return AwadDDoSTopology
