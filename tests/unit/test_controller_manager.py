import pytest

from unittest.mock import Mock, MagicMock

from infrastructure.controller_manager import ControllerManager
from tests.dummies.dummy_controller import DummyController


@pytest.fixture
def controller_manager():
    context = Mock()
    manager = ControllerManager(DummyController, context)
    yield manager

    if manager.is_running:
        manager.stop()

@pytest.fixture
def fake_socket(monkeypatch):
    import socket

    sock = MagicMock()

    sock.__enter__.return_value = sock

    monkeypatch.setattr(
        socket,
        'socket',
        MagicMock(return_value=sock)
    )

    return sock


class TestIsRunning:

    def test_running_property_is_false_initially(self, controller_manager):
        assert controller_manager.is_running is False

    def test_running_property_is_true_when_process_exists(self, controller_manager):
        controller_manager._process = Mock()
        assert controller_manager.is_running is True

class TestStart:

    def test_start_stores_controller_process(self, monkeypatch, controller_manager):
        process = Mock()

        monkeypatch.setattr(
            controller_manager,
            '_launch_controller',
            Mock(return_value=process)
        )

        monkeypatch.setattr(
            controller_manager,
            '_wait_until_ready',
            Mock()
        )

        controller_manager.start()
        assert controller_manager._process is process

    def test_start_raises_if_controller_is_already_running(self, controller_manager):
        controller_manager._process = Mock()
        with pytest.raises(RuntimeError, match='Controller already running. Terminate before re-launching'):
            controller_manager.start()

    def test_start_propagates_controller_startup_failure(self, monkeypatch, controller_manager):
        process = Mock()

        monkeypatch.setattr(
            controller_manager,
            '_launch_controller',
            Mock(return_value=process)
        )

        monkeypatch.setattr(
            controller_manager,
            '_wait_until_ready',
            Mock(side_effect=RuntimeError())
        )

        with pytest.raises(RuntimeError):
            controller_manager.start()


class TestWaitUntilReady:

    def test_start_asks_to_wait(self, monkeypatch, controller_manager):
        process = Mock()
        launch = Mock(return_value=process)
        wait = Mock()

        monkeypatch.setattr(
            controller_manager,
            '_launch_controller',
            launch
        )

        monkeypatch.setattr(
            controller_manager,
            '_wait_until_ready',
            wait
        )

        controller_manager.start()
        wait.assert_called_once()

    def test_wait_until_ready_returns_when_controller_becomes_ready(self, controller_manager, monkeypatch):
        monkeypatch.setattr(
            controller_manager,
            '_is_process_alive',
            Mock(return_value=True)
        )

        monkeypatch.setattr(
            controller_manager,
            '_is_controller_ready',
            Mock(side_effect=[False, False, True])
        )

        monkeypatch.setattr('time.sleep', Mock())
        monkeypatch.setattr('time.monotonic', lambda: 0)

        controller_manager._wait_until_ready()

        assert controller_manager._is_controller_ready.call_count == 3

    def test_wait_until_ready_raises_if_process_dies(self, controller_manager, monkeypatch):
        controller_manager._process = Mock(returncode=1)

        monkeypatch.setattr(
            controller_manager,
            '_is_process_alive',
            Mock(side_effect=[True, True, False])
        )

        monkeypatch.setattr(
            controller_manager,
            '_is_controller_ready',
            Mock(return_value=False)
        )

        monkeypatch.setattr('time.sleep', Mock())
        monkeypatch.setattr('time.monotonic', lambda: 0)

        with pytest.raises(RuntimeError):
            controller_manager._wait_until_ready()

    def test_raises_after_timeout(self, controller_manager, monkeypatch):
        monkeypatch.setattr(
            controller_manager,
            '_is_process_alive',
            Mock(return_value=True)
        )

        monkeypatch.setattr(
            controller_manager,
            '_is_controller_ready',
            Mock(return_value=False)
        )

        monkeypatch.setattr(
            controller_manager,
            '_timed_out',
            Mock(side_effect=[False, False, True])
        )

        monkeypatch.setattr('time.sleep', Mock())

        with pytest.raises(TimeoutError):
            controller_manager._wait_until_ready()


class TestControllerReady:

    def test_returns_true_when_controller_signals_ready(self, controller_manager, fake_socket):
        fake_socket.recv.return_value = b'READY'

        assert controller_manager._is_controller_ready('/temp/controller.sock')
        fake_socket.connect.assert_called_once_with( '/temp/controller.sock')
        fake_socket.recv.assert_called_once_with(1024)

    def test_returns_false_when_socket_does_not_exist(self, controller_manager, fake_socket):
        fake_socket.connect.side_effect = FileNotFoundError

        assert not controller_manager._is_controller_ready('/tmp/controller.sock')
        fake_socket.recv.assert_not_called()

    def test_returns_false_for_any_response_other_than_ready(self, controller_manager, fake_socket):
        for response in [b'any', b'other', b'stuff']:
            fake_socket.recv.return_value = response
            assert not controller_manager._is_controller_ready('/tmp/controller.sock')

class TestStop:

    def test_stop_terminates_controller(self, controller_manager):
        process = Mock()
        controller_manager._process = process
        controller_manager.stop()

        process.terminate.assert_called_once()
        process.wait.assert_called_once()

    def test_stop_without_running_controller_does_not_fail(self, controller_manager):
        controller_manager.stop()

    def test_stop_clears_process_reference(self, controller_manager):
        process = Mock()
        controller_manager._process = process
        controller_manager.stop()

        assert controller_manager._process is None
