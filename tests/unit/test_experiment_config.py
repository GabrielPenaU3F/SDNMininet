from config.experiment_config import ExperimentConfig


class TestExperimentConfig:

    def test_from_args_passes_arguments(self, args_namespace):
        experiment_config = ExperimentConfig.from_args(args_namespace)
        assert experiment_config.duration == args_namespace.duration
        assert experiment_config.seed == args_namespace.seed
        assert experiment_config.sampling_interval == args_namespace.sampling_interval
        assert experiment_config.experiment_root == args_namespace.experiment_path / args_namespace.experiment

    def test_uses_given_experiment_root(self, experiment_config, tmp_path):
        assert experiment_config.experiment_root == tmp_path / 'dummy_experiment'

    def test_measurements_path_is_inside_experiment_root(self, experiment_config, tmp_path):
        expected = tmp_path / 'dummy_experiment' / 'measurements'
        assert experiment_config.measurements_path == expected

    def test_init_creates_experiment_directory(self, args_namespace, tmp_path):
        assert not (tmp_path / 'dummy_experiment').exists()
        ExperimentConfig('dummy_experiment', experiment_root=tmp_path)
        assert (tmp_path / 'dummy_experiment').exists()

    def test_creates_measurements_directory(self, args_namespace, tmp_path):
        assert not (tmp_path / 'dummy_experiment' / 'measurements').exists()
        ExperimentConfig('dummy_experiment', experiment_root=tmp_path)
        assert (tmp_path / 'dummy_experiment' / 'measurements').exists()
