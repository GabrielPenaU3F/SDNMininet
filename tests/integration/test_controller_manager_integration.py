from config.experiment_config import ExperimentConfig
from controllers.base_controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self, tmp_path):
        config = ExperimentConfig('dummy_experiment', experiment_root=tmp_path) # To ensure directories are created
        with config.config_context():
            config.write_config_file()
            manager = ControllerManager(BaseController)
            manager.start(config)
            assert manager.is_running
            manager.stop()
            assert not manager.is_running
