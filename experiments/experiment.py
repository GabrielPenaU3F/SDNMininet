from abc import ABC, abstractmethod

import mininet.clean as mn_clean

from infrastructure.controller_manager import ControllerManager
from infrastructure.network_management import build_network


class Experiment(ABC):

    def __init__(self, **kwargs):
        self.network_mgr = None
        self.controller_mgr = ControllerManager(self.controller_cls, **kwargs)

        self.net = None

    def execute(self):
        self.deploy_infrastructure()
        try:
            self.run()
        finally:
            self.shutdown()

    def deploy_infrastructure(self, **kwargs):
        self._clean_sdn()
        self.controller_mgr.start()
        self.net = build_network(self.topology_cls, **kwargs)
        self.net.start()

    def shutdown(self):

        if self.net is not None:
            self.net.stop()

        self.controller_mgr.stop()

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
