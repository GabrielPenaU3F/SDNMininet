from experiments.experiment import Experiment
from experiments.experiment_debug.debug_controller import DebugController
from hosts.host_apps.minimal_apps import SilentListenerHostApp, DeafSpeakerHostApp
from topologies.simple_topology import SimpleTopology


class ExperimentDebug(Experiment):

    def _begin(self):
        speaker = self.network_mgr.host('h1')
        listener = self.network_mgr.host('h2')

        listener.launch_app(
            SilentListenerHostApp,
            self.app_context,
            port=100
        )

        # stdout = open('experiments/experiment_debug/debug.out', 'w')
        # stderr = open('experiments/experiment_debug/debug.err', 'w')
        # tcpdump = speaker.popen(
        #     'tcpdump',
        #     '-n',
        #     '-i', 'h1-eth0',
        #     'udp',
        #     'port', '100',
        #     stdout=stdout,
        #     stderr=stderr,
        # )
        # stdout.close()
        # stderr.close()

        speaker.launch_app(
            DeafSpeakerHostApp,
            self.app_context,
            dst_ip=listener.ip,
            port=100
        )

    @property
    def controller_cls(self):
        return DebugController

    @property
    def topology_cls(self):
        return SimpleTopology
