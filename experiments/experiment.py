import time
from abc import ABC, abstractmethod

import mininet.clean as mn_clean

from infrastructure.controller_manager import ControllerManager

from infrastructure.network_manager import NetworkManager


class Experiment(ABC):

    def __init__(self, **kwargs):
        self.network_mgr = NetworkManager(self.topology_cls, **kwargs)
        self.controller_mgr = ControllerManager(self.controller_cls, **kwargs)

    def execute(self, duration):
        self.deploy_infrastructure()
        try:
            self.run()
            self._wait_until_finished(duration)
        finally:
            self.shutdown()

    def deploy_infrastructure(self, **kwargs):
        self._clean_sdn()
        self.controller_mgr.start()
        self.network_mgr.build_network(**kwargs)
        self.network_mgr.start()

    def shutdown(self):
        self.network_mgr.stop()
        self.controller_mgr.stop()

    def _clean_sdn(self):
        mn_clean.cleanup()

    def _wait_until_finished(self, duration):
        deadline = time.monotonic() + duration

        while time.monotonic() < deadline:
            time.sleep(0.5)

    @property
    def net(self):
        return self.network_mgr.net

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
