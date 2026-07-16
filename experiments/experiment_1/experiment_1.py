import numpy as np

from controllers.base_controller.controller import BaseController
from experiments.experiment import Experiment
from topologies.awad_topology import AwadDDoSTopology

'''

DESCRIPTION

8 sources emmit Poisson, traffic, each one with a
random rate sampled from a U[0, 10] distribution.

'''

class Experiment1(Experiment):

    def run(self):
        h1 = self.net['h1']
        h2 = self.net['h2']

        rate_1, rate_2 = np.random.uniform(0, 10, 2)

        self.program_launcher.launch(h1,
                                     script_path='/experiments/experiment_1/host_program.py',
                                     dst_ip='10.0.0.2', port='100', rate=rate_1)
        self.program_launcher.launch(h2,
                                     script_path='/experiments/experiment_1/host_program.py',
                                     dst_ip='10.0.0.1', port='100', rate=rate_2)


    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return AwadDDoSTopology
