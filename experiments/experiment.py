import time
from abc import ABC, abstractmethod

import mininet.clean as mn_clean

from infrastructure.controller_manager import ControllerManager

from infrastructure.network_manager import NetworkManager
from launchers.host_program_launcher import HostProgramLauncher


class Experiment(ABC):

    def __init__(self, context, **kwargs):
        self.context = context
        self.program_launcher = HostProgramLauncher(self.context)
        self.network_mgr = NetworkManager(self.topology_cls, **kwargs)
        self.controller_mgr = ControllerManager(self.controller_cls, context, **kwargs)

    def execute(self):
        self.deploy_infrastructure()
        try:
            self.run()
            self._wait_until_finished()
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

    @staticmethod
    def _clean_sdn():
        mn_clean.cleanup()

    def _wait_until_finished(self):
        deadline = time.monotonic() + self.context.duration

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
