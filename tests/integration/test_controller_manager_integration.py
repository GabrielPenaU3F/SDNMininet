from config.experiment_config import ExperimentConfig
from controllers.base_controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self, tmp_path):
        config = ExperimentConfig('dummy_experiment', experiment_root=tmp_path) # To ensure directories are created
        try:
            config.write_config_file()
            experiment_root = tmp_path / 'dummy_experiment'
            manager = ControllerManager(BaseController, experiment_root)
            manager.start()
            assert manager.is_running
            manager.stop()
            assert not manager.is_running

        finally:
            config.delete_config_file()
