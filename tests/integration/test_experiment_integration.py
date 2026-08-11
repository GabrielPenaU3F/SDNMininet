from pathlib import Path

from experiments.experiment_debug.experiment_debug import ExperimentDebug
from tests.utilities.dummy_experiments import IntegrationTestExperiment, SamplingIntervalExperiment, \
    HostAppIntegrationExperiment


class TestExperimentIntegration:

    def test_experiment_deploys_real_infrastructure(self, make_experiment, tmp_path):
        experiment = make_experiment(IntegrationTestExperiment)
        experiment.execute()
        file = Path(tmp_path / 'dummy_experiment' / 'measurements' / 'test_file')

        assert file.exists()

        with open(str(file), 'r') as f:
            line = f.readline()
        assert line.rstrip() == 'Debugging...'

    def test_controller_receives_sampling_interval(self, make_experiment, tmp_path):
        experiment = make_experiment(
            SamplingIntervalExperiment,
            sampling_interval=0.05,
            duration=0.5,
        )

        experiment.execute()

        file = tmp_path / 'dummy_experiment' / 'measurements' / 'test_file'
        with open(str(file), 'r') as f:
            _ = f.readline()
            line_2 = f.readline()
        assert line_2.rstrip() == 'SI=0.05'

    def test_experiment_hosts_redirect_console_outputs(self, make_experiment, tmp_path):
        experiment = make_experiment(
            ExperimentDebug,
            sampling_interval=0.05,
            duration=0.1,
        )

        experiment.execute()
        stdout_dir = experiment.config.stdout_path

        for host in ('h1', 'h2'):
            stderr = stdout_dir / f'{host}.err'
            stdout = stdout_dir / f'{host}.out'
            assert stderr.exists()
            assert stdout.exists()

    def test_host_app_runs_inside_experiment_root(self, make_experiment):
        experiment = make_experiment(HostAppIntegrationExperiment)
        experiment.execute()

        with open(Path(experiment.config.experiment_root / 'logs' / 'logfile.log')) as f:
            assert f.readline() == 'ok'

    def test_experiment_shuts_down_cleanly(self, make_experiment, tmp_path):
        experiment = make_experiment(
            ExperimentDebug,
            sampling_interval=0.05,
            duration=1,
        )

        experiment.execute()
        stdout_dir = experiment.config.stdout_path

        for host in ('h1', 'h2'):
            stderr = stdout_dir / f'{host}.err'
            content = stderr.read_text()

            assert 'Traceback' not in content, \
                f'{host} crashed:\n{content}'

            assert 'Network is unreachable' not in content, \
                f'{host} attempted to use the network after shutdown:\n{content}'

            assert content == ''
