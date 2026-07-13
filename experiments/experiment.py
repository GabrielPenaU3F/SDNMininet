from abc import ABC, abstractmethod

import mininet.clean as mn_clean

from infrastructure.controller_management import start_controller, stop_controller
from infrastructure.network_management import build_network


class Experiment(ABC):

    def __init__(self):
        self.net = None
        self.controller = None

    def execute(self):
        self.deploy_infrastructure()
        try:
            self.run()
        finally:
            self.shutdown()

    def deploy_infrastructure(self, **kwargs):
        self._clean_sdn()
        self.controller = start_controller(self.controller_cls, **kwargs)
        self.net = build_network(self.topology_cls, **kwargs)
        self.net.start()

    def shutdown(self):

        if self.net is not None:
            self.net.stop()

        if self.controller is not None:
            stop_controller(self.controller)

    def _clean_sdn(self):
        mn_clean.cleanup()

    # === To be implemented by each subclass ===

    @abstractmethod
    def run(self):
        pass

    @property
    @abstractmethod
    def controller_cls(self):
        pass

    @property
    @abstractmethod
    def topology_cls(self):
        pass


