from core.config.environment import Environment
from core.controllers.debug_controller import DebugController
from experiments.experiment import Experiment
from topologies.simple_topology import SimpleTopology


class ExperimentDebug(Experiment):

    def begin(self):
        h1 = self.network_mgr.host('h1')
        h2 = self.network_mgr.host('h2')

        path = Environment.get_environment().host_programs_path

        self.program_launcher.launch(
            h2,
            script_path=path / "debug_receiver.py"
        )

        self.program_launcher.launch(
            h1,
            script_path=path / 'debug_sender.py'
        )

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
