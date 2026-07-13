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

        network = Mock()
        dummy_experiment.controller_mgr = Mock()

        monkeypatch.setattr(
            experiment_module,
            "build_network",
            Mock(return_value=network)
        )

        monkeypatch.setattr(
            dummy_experiment,
            "_clean_sdn",
            Mock()
        )

        dummy_experiment.deploy_infrastructure()

        dummy_experiment._clean_sdn.assert_called_once()
        dummy_experiment.controller_mgr.start.assert_called_once()

        experiment_module.build_network.assert_called_once_with(
            dummy_experiment.topology_cls
        )

        network.start.assert_called_once()
        assert dummy_experiment.net is network

    def test_shutdown(self, dummy_experiment):
        dummy_experiment.controller_mgr = Mock()

        network = Mock()
        dummy_experiment.net = network

        dummy_experiment.shutdown()

        network.stop.assert_called_once()
        dummy_experiment.controller_mgr.stop.assert_called_once()

    def test_shutdown_is_called_even_if_run_fails(self, failing_experiment):
        failing_experiment.deploy_infrastructure = Mock()
        failing_experiment.shutdown = Mock()

        with pytest.raises(RuntimeError):
            failing_experiment.execute()

        failing_experiment.shutdown.assert_called_once()

    def test_shutdown_without_network(self, dummy_experiment):
        dummy_experiment.net = None
        dummy_experiment.controller_mgr = Mock()

        dummy_experiment.shutdown()

        dummy_experiment.controller_mgr.stop.assert_called_once()
