from experiments.experiment import Experiment
from tests.dummies.dummy_controller import DummyController


class DummyExperiment(Experiment):

    controller_cls = DummyController
    topology_cls = object

    def __init__(self):
        super().__init__()
        self.run_called = False

    def run(self):
        self.run_called = True


class FailingExperiment(Experiment):

    controller_cls = DummyController
    topology_cls = object

    def run(self):
        raise RuntimeError("boom")
