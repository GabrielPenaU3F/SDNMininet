import time
from pathlib import Path

import pytest
import csv

from controllers.base_controller.controller import BaseController
from experiments.experiment import Experiment
from src.config.environment import Environment
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
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def run(self):
        h1 = self.net.get("h1")
        h1.cmd("ping -c 3 h2")
        time.sleep(2)


@pytest.fixture
def experiment(tmp_path):
    tmp_root = tmp_path / 'fake_project'
    Environment._reset_instance()
    Environment.instance = Environment(project_root=tmp_root)
    exp = IntegrationTestExperiment()
    return exp


class TestExperimentIntegration:


    def test_experiment_deploys_real_infrastructure(self):
        exp = IntegrationTestExperiment()
        exp.execute(duration=1)

        stats_csv = Path(Environment.get_environment().traffic_stats_file)
        assert stats_csv.exists()
        assert csv_has_at_least_one_data_row(stats_csv)