import re
from argparse import Namespace

from core.config.experiment_config import ExperimentConfig
from tests.utilities.dummy_experiments import MacLearningIntegrationExperiment


def get_mac_flow(flows, mac):
    return next(
        flow for flow in flows
        if flow.match.get('eth_dst') == mac
    )

def parse_mac_installing_rules(log):
    rules = re.findall(
        r'Installing rule: dst=([^,]+), out_port=(\d+)',
        log.read_text()
    )
    rules = {
        mac: int(port)
        for mac, port in rules
    }
    return rules

class TestControllerIntegration:

    def test_switch_learns_macs(self, tmp_path):
        args = Namespace(experiment='dummy_experiment', duration=1, seed=42, experiment_path=tmp_path,
                         sampling_interval=1.0)
        config = ExperimentConfig.from_args(args)
        experiment = MacLearningIntegrationExperiment(config)

        # Controlled execution
        with experiment.config.config_context():
            experiment.deploy_infrastructure()
            try:
                h1 = experiment.network_mgr.host('h1')
                h2 = experiment.network_mgr.host('h2')
                mac_h1 = h1.mac
                mac_h2 = h2.mac
                experiment._begin()
                experiment._wait_until_finished()
            finally:
                experiment.shutdown()

        log = experiment.config.logs_path / 'controller.log'
        rules = parse_mac_installing_rules(log)

        assert rules == {
            mac_h1: 1,
            mac_h2: 2,
        }
