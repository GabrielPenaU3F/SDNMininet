from controllers.base_controller.controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self):
        manager = ControllerManager(BaseController)
        manager.start()
        assert manager.is_running
        manager.stop()
        assert not manager.is_running
