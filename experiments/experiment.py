import time
from abc import ABC, abstractmethod

import numpy as np

from core.controller_manager import ControllerManager

from core.network_manager import NetworkManager
from hosts.host_apps.host_app import HostAppContext


class Experiment(ABC):

    def __init__(self, config, **kwargs):
        self.config = config
        self.rng = np.random.default_rng(seed=self.config.seed)
        self.network_mgr = NetworkManager(self.topology_cls)
        self.controller_mgr = ControllerManager(self.controller_cls)
        self.app_context = HostAppContext(
            experiment_root=config.experiment_root,
            stdout_path=config.stdout_path
        )

    def execute(self):
        with self.config.config_context():
            try:
                self.deploy_infrastructure()
                self._begin()
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
        if self.config.duration >= 0:
            deadline = time.monotonic() + self.config.duration
        else: deadline = np.inf

        while time.monotonic() < deadline:
            time.sleep(0.5)

    # === To be implemented by each subclass ===

    @abstractmethod
    def _begin(self):
        pass

    @property
    @abstractmethod
    def controller_cls(self):
        pass

    @property
    @abstractmethod
    def topology_cls(self):
        pass
