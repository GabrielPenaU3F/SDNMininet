from config.environment import Environment
from controllers.debug_controller import DebugController
from experiments.experiment import Experiment
from topologies.simple_topology import SimpleTopology


class ExperimentDebug(Experiment):

    def begin(self):
        h1 = self.net["h1"]
        h2 = self.net["h2"]

        path = Environment.get_environment().shared_host_programs_path

        self.program_launcher.launch(
            h2,
            script_path=path / "debug_receiver.py"
        )

        self.program_launcher.launch(
            h1,
            script_path=path / "debug_sender.py"
        )

        # sender, receiver = (self.net['h1'], self.net['h2'])
        # rate = 10
        # seed = 1
        #
        # path = Environment.get_environment().shared_host_programs_path
        # sender_script = path / 'poisson_udp_host_program.py'
        # receiver_script = path / 'silent_receiver_host_program.py'
        #
        # # Sender
        # self.program_launcher.launch(sender, script_path=sender_script,
        #                              dst_ip=receiver.IP(),
        #                              port='100',
        #                              rate=rate,
        #                              seed=seed)
        #
        # # Receiver
        # self.program_launcher.launch(receiver, script_path=receiver_script, port='100')

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
