import time
from pathlib import Path

import csv

import pandas as pd

from controllers.base_controller import BaseController
from experiments.experiment import Experiment
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
        h1 = self.net.get('h1')
        h1.cmd('ping -c 3 h2')
        time.sleep(2)


class SamplingIntervalExperiment(Experiment):

    @property
    def controller_cls(self):
        return BaseController

    @property
    def topology_cls(self):
        return SimpleTopology

    def run(self):
        time.sleep(0.5)


class TestExperimentIntegration:

    def test_experiment_deploys_real_infrastructure(self, make_experiment, tmp_path):
        experiment = make_experiment(IntegrationTestExperiment)
        experiment.execute()
        stats_csv = Path(tmp_path / 'dummy_experiment' / 'measurements' / 'traffic_stats.csv')

        assert stats_csv.exists()
        assert csv_has_at_least_one_data_row(stats_csv)

    def test_controller_receives_sampling_interval(self, make_experiment, tmp_path):
        experiment = make_experiment(
            SamplingIntervalExperiment,
            sampling_interval=0.05,
            duration=0.5,
            experiment_root=tmp_path,
        )

        experiment.execute()
        df = pd.read_csv(
            experiment.config.measurements_path / 'traffic_stats.csv'
        )

        assert df['poll_id'].max() > 10 # should be a large number of polls