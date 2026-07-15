from config.execution_context import ExecutionContext
from controllers.base_controller.controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self):
        context = ExecutionContext(duration=0.001, seed=42)
        manager = ControllerManager(BaseController, context)
        manager.start()
        assert manager.is_running
        manager.stop()
        assert not manager.is_running
