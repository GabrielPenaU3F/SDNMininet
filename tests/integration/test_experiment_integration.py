import time
from pathlib import Path

import pytest
import csv

from config.execution_context import ExecutionContext
from controllers.base_controller.controller import BaseController
from experiments.experiment import Experiment
from config.environment import Environment
from topologies.simple_topology import SimpleTopology


def csv_has_at_least_one_data_row(path):
    with open(path, newline='') as file:
        reader = csv.reader(file)

        next(reader, None)  # Header

        first_row = next(reader, None)

    return first_row is not None and any(field.strip() for field in first_row)


class IntegrationTestExperiment(Experiment):

    @property
    def controller_cls(self):
        print(BaseController.__module__)
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def run(self):
        h1 = self.net.get('h1')
        h1.cmd('ping -c 3 h2')
        time.sleep(2)


@pytest.fixture
def experiment(tmp_path):
    tmp_root = tmp_path / "fake_project"

    Environment._reset_instance()
    Environment.instance = Environment(
        project_root=None,
        experiment_root=tmp_root
    )

    context = ExecutionContext(
        duration=0.001,
        seed=42,
        experiment_root=tmp_root,
    )

    return IntegrationTestExperiment(context)

class TestExperimentIntegration:

    def test_experiment_deploys_real_infrastructure(self, experiment, tmp_path):
        experiment.execute()
        stats_csv = Path(tmp_path / 'fake_project' / 'measurements' / 'traffic_stats.csv')

        assert stats_csv.exists()
        # assert csv_has_at_least_one_data_row(stats_csv)
