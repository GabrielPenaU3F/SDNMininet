from unittest.mock import Mock

import pytest

from config.execution_context import ExecutionContext
from tests.dummies.dummy_experiment import DummyExperiment, FailingExperiment


@pytest.fixture
def dummy_experiment(execution_context):
    return DummyExperiment(execution_context)

@pytest.fixture
def failing_experiment(execution_context):
    return FailingExperiment(execution_context)

@pytest.fixture
def make_dummy_experiment_with_duration():
    def _make(duration):
        context = ExecutionContext(
            duration=duration,
            seed=42
        )
        return DummyExperiment(context)
    return _make


class TestExperiment:

    def test_experiment_runs(self, dummy_experiment):
        dummy_experiment.deploy_infrastructure = Mock()
        dummy_experiment.shutdown = Mock()
        dummy_experiment.execute()
        assert dummy_experiment.run_called is True

    def test_deploy_infrastructure(self, monkeypatch, dummy_experiment):

        dummy_experiment.controller_mgr = Mock()
        dummy_experiment.network_mgr = Mock()

        monkeypatch.setattr(
            dummy_experiment,
            '_clean_sdn',
            Mock()
        )

        dummy_experiment.deploy_infrastructure()

        dummy_experiment._clean_sdn.assert_called_once()
        dummy_experiment.controller_mgr.start.assert_called_once()
        dummy_experiment.network_mgr.build_network.assert_called_once()
        dummy_experiment.network_mgr.start.assert_called_once()

    def test_shutdown(self, dummy_experiment):
        dummy_experiment.controller_mgr = Mock()
        dummy_experiment.network_mgr = Mock()

        dummy_experiment.shutdown()

        dummy_experiment.network_mgr.stop.assert_called_once()
        dummy_experiment.controller_mgr.stop.assert_called_once()

    def test_shutdown_is_called_even_if_run_fails(self, failing_experiment):
        failing_experiment.deploy_infrastructure = Mock()
        failing_experiment.shutdown = Mock()

        with pytest.raises(RuntimeError):
            failing_experiment.execute()

        failing_experiment.shutdown.assert_called_once()

    def test_shutdown_without_network(self, dummy_experiment):
        dummy_experiment.controller_mgr = Mock()
        dummy_experiment.shutdown()
        dummy_experiment.controller_mgr.stop.assert_called_once()


class TestWaitUntilFinished:

    def test_wait_until_finished_sleeps_until_duration_expires(self, monkeypatch, make_dummy_experiment_with_duration):

        dummy_experiment = make_dummy_experiment_with_duration(1.0)
        monotonic = Mock(side_effect=[
            0.0,   # deadline = 1.0
            0.0,   # while -> in
            0.5,   # while -> in
            1.0    # while -> out
        ])

        sleep = Mock()

        monkeypatch.setattr('time.monotonic', monotonic)
        monkeypatch.setattr('time.sleep', sleep)

        dummy_experiment._wait_until_finished()

        assert sleep.call_count == 2
        sleep.assert_called_with(0.5)

    def test_wait_until_finished_returns_immediately_if_duration_is_zero(self, monkeypatch, make_dummy_experiment_with_duration):
        dummy_experiment = make_dummy_experiment_with_duration(0)
        monotonic = Mock(side_effect=[
            0.0,   # deadline
            0.0    # time
        ])

        sleep = Mock()

        monkeypatch.setattr('time.monotonic', monotonic)
        monkeypatch.setattr('time.sleep', sleep)
        dummy_experiment._wait_until_finished()
        sleep.assert_not_called()

