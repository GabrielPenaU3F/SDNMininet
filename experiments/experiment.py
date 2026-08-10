import time
from abc import ABC, abstractmethod

import numpy as np

from core.controller_manager import ControllerManager
from core.launchers.host_app_launcher import HostAppLauncher

from core.network_manager import NetworkManager


class Experiment(ABC):

    def __init__(self, config, **kwargs):
        self.config = config
        self.rng = np.random.default_rng(seed=self.config.seed)
        self.app_launcher = HostAppLauncher(self.config)
        self.network_mgr = NetworkManager(self.topology_cls)
        self.controller_mgr = ControllerManager(self.controller_cls)

    def execute(self):
        with self.config.config_context():
            self.deploy_infrastructure()
            try:
                self.begin()
                self._wait_until_finished()
            finally:
                self.shutdown()

    def deploy_infrastructure(self, **kwargs):
        self.controller_mgr.start(self.config)
        self.network_mgr.deploy_network(**kwargs)

    def shutdown(self):
        self.network_mgr.destroy_network()
        self.controller_mgr.stop()

    def _wait_until_finished(self):
        deadline = time.monotonic() + self.config.duration

        while time.monotonic() < deadline:
            time.sleep(0.5)

    # === To be implemented by each subclass ===

    @abstractmethod
    def begin(self):
        pass

    @property
    @abstractmethod
    def controller_cls(self):
        pass

    @property
    @abstractmethod
    def topology_cls(self):
        pass
