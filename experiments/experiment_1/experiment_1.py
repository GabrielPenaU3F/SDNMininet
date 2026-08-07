import numpy as np

from core.config.environment import Environment
from experiments.experiment_1.exp1_controller import Experiment1Controller
from experiments.experiment import Experiment
from topologies.awad_topology import AwadDDoSTopology

'''

DESCRIPTION

8 sources emmit Poisson, traffic, each one with a
random rate sampled from a U[30, 60] distribution.

'''

class Experiment1(Experiment):

    def begin(self):
        hosts = [self.net['h1'], self.net['h2'], self.net['h3'], self.net['h4'],
                 self.net['h5'], self.net['h6'], self.net['h7'], self.net['h8']]
        rates = self.rng.uniform(0, 10, 8)
        receivers = set(hosts.copy())

        parent_ss = np.random.SeedSequence(self.config.seed)
        host_seeds = [
            int(np.random.default_rng(ss).integers(2 ** 32))
            for ss in parent_ss.spawn(8)
        ]

        for i in range(8):
            h = hosts[i]
            script = (Environment.get_environment().host_programs_path /
                      'poisson_udp_host_program.py')
            candidates = [r for r in receivers if r is not h]
            target = self.rng.choice(candidates)
            receivers.remove(target)
            # print(h.name, target.IP(), rates[i], host_seeds[i])
            self.program_launcher.launch(h, script_path=script,
                                         dst_ip=target.IP(),
                                         port='100',
                                         rate=rates[i],
                                         seed=host_seeds[i])

    @property
    def controller_cls(self):
        return Experiment1Controller

    @property
    def topology_cls(self):
        return AwadDDoSTopology
