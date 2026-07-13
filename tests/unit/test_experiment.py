from unittest.mock import Mock

import pytest

from tests.dummies.dummy_experiment import DummyExperiment, FailingExperiment


@pytest.fixture
def dummy_experiment():
    return DummyExperiment()

@pytest.fixture
def failing_experiment():
    return FailingExperiment()

class TestExperiment:

    def test_experiment_runs(self, dummy_experiment):
        dummy_experiment.deploy_infrastructure = Mock()
        dummy_experiment.shutdown = Mock()
        dummy_experiment.execute()
        assert dummy_experiment.run_called is True

    def test_deploy_infrastructure(self, monkeypatch, dummy_experiment):
        import experiments.experiment as experiment_module

        controller = Mock()
        network = Mock()
        start_controller = Mock(return_value=controller)
        build_network = Mock(return_value=network)

        monkeypatch.setattr(
            experiment_module,
            'start_controller',
            start_controller
        )

        monkeypatch.setattr(
            experiment_module,
            'build_network',
            build_network
        )

        dummy_experiment.deploy_infrastructure()

        start_controller.assert_called_once()
        build_network.assert_called_once()
        network.start.assert_called_once()

        assert dummy_experiment.controller is controller
        assert dummy_experiment.net is network

    def test_shutdown(self, monkeypatch, dummy_experiment):
        import experiments.experiment as experiment_module

        controller = Mock()
        network = Mock()

        stop_controller = Mock()

        monkeypatch.setattr(
            experiment_module,
            'stop_controller',
            stop_controller
        )

        dummy_experiment.controller = controller
        dummy_experiment.net = network

        dummy_experiment.shutdown()

        network.stop.assert_called_once()
        stop_controller.assert_called_once_with(controller)

    def test_shutdown_is_called_even_if_run_fails(self, failing_experiment):
        failing_experiment.deploy_infrastructure = Mock()
        failing_experiment.shutdown = Mock()

        with pytest.raises(RuntimeError):
            failing_experiment.execute()

        failing_experiment.shutdown.assert_called_once()
