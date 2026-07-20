from controllers.base_controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self, experiment_config):
        manager = ControllerManager(BaseController, experiment_config)
        manager.start()
        assert manager.is_running
        manager.stop()
        assert not manager.is_running
