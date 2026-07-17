from config.execution_context_factory import ExecutionContextFactory
from controllers.base_controller import BaseController
from infrastructure.controller_manager import ControllerManager


class TestControllerManagerIntegration:

    def test_controller_manager_starts_real_controller(self, context_args):
        context = ExecutionContextFactory().make_context(context_args)
        manager = ControllerManager(BaseController, context)
        manager.start()
        assert manager.is_running
        manager.stop()
        assert not manager.is_running
