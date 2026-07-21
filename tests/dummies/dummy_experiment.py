from experiments.experiment import Experiment
from tests.dummies.dummy_controller import DummyController
from tests.dummies.dummy_topology import DummyTopology


class DummyExperiment(Experiment):

    controller_cls = DummyController
    topology_cls = DummyTopology

    def __init__(self, config):
        super().__init__(config)
        self.run_called = False

    def begin(self):
        self.run_called = True


class FailingExperiment(Experiment):

    controller_cls = DummyController
    topology_cls = DummyTopology

    def begin(self):
        raise RuntimeError('boom')
