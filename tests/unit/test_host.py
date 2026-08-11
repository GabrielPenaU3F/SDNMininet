from pathlib import Path

import pytest

from unittest.mock import Mock, call

from core.config.environment import Environment
from hosts.host import Host
from hosts.host_apps.host_app import HostAppContext
from tests.utilities.dummy_host_apps import DummyTestHostApp


@pytest.fixture
def dummy_mn_host():
    mn_host = Mock()
    mn_host.name = 'h1'
    mn_host.IP.return_value = '127.0.0.1'
    process = Mock()
    process.poll.return_value = None
    mn_host.popen.return_value = process
    return mn_host

@pytest.fixture
def example_host(dummy_mn_host):
    return Host(dummy_mn_host)

@pytest.fixture
def example_context(tmp_path):
    return HostAppContext(experiment_root=tmp_path, stdout_path=tmp_path)


class TestHost:

    def test_host_wraps_around_mininet_host(self, example_host):
        assert example_host.name == 'h1'
        assert example_host.ip == '127.0.0.1'

    def test_cmd_delegates_to_mininet_host(self):
        mn_host = Mock()
        mn_host.cmd.return_value = 'result'

        host = Host(mn_host)
        result = host.cmd('ping', '-c', '3', 'h2')

        assert result == 'result'
        mn_host.cmd.assert_called_once_with('ping', '-c', '3', 'h2')

    def test_popen_delegates_to_mininet_host(self):
        mn_host = Mock()
        process = Mock()
        mn_host.popen.return_value = process

        host = Host(mn_host)
        result = host.popen('python', 'script.py', foo='bar')

        assert result is process
        mn_host.popen.assert_called_once_with(
            'python',
            'script.py',
            foo='bar'
        )


class TestProcessRunning:

    def test_process_running_is_false_when_no_process_exists(self, example_host):
        assert not example_host.process_running

    def test_process_running_is_true_while_process_is_running(self, example_host, example_context):
        process = Mock()
        process.poll.return_value = None
        example_host.process = process
        assert example_host.process_running
        example_host.process.poll.assert_called_once()

    def test_process_running_is_false_when_process_has_finished_correctly(self, example_host):
        process = Mock()
        process.poll.return_value = 0
        example_host.process = process

        assert not example_host.process_running

    def test_process_running_is_false_when_process_has_failed(self, example_host):
        process = Mock()
        process.poll.return_value = 1
        example_host.process = process

        assert not example_host.process_running


class TestWait:

    def test_wait_waits_for_process(self, example_host):
        process = Mock()
        process.wait.return_value = 0
        example_host.process = process
        result = example_host.wait()

        assert result == 0
        process.wait.assert_called_once()

    def test_wait_does_nothing_when_there_is_no_process(self, example_host):
        assert example_host.wait() is None


class TestStop:

    def test_stop_terminates_process_and_waits_for_it(self, example_host):
        process = Mock()
        example_host.process = process
        example_host._stop()

        process.terminate.assert_called_once()
        process.wait.assert_called_once()

    def test_stop_terminates_process_before_waiting(self, example_host):
        process = Mock()
        example_host.process = process
        example_host._stop()

        assert process.method_calls == [
            call.terminate(),
            call.wait()
        ]

    def test_stop_does_nothing_when_there_is_no_process(self, example_host):
        example_host._stop()

        assert example_host.process is None

    def test_stop_clears_app_process_and_actually_stops(self, example_host, example_context):
        example_host.launch_app(DummyTestHostApp, example_context)
        example_host._stop()

        assert example_host.app is None
        assert example_host.process is None
        assert not example_host.process_running


class TestLaunchApp:

    def test_launch_stores_app_and_process(self, example_host, example_context):
        example_host.launch_app(DummyTestHostApp,
                                example_context,
                                argument=1)

        assert type(example_host.app) is DummyTestHostApp
        assert example_host.app.argument == 1
        assert example_host.process is example_host.mn_host.popen.return_value

    def test_launch_invokes_popen_with_expected_command(self, example_host, example_context):
        example_host.launch_app(
            DummyTestHostApp,
            example_context,
            argument=1
        )
        args, kwargs = example_host.mn_host.popen.call_args
        command = args[0]

        assert command[0] == str(Environment.get_environment().python_path)
        assert Path(command[1]).name == 'host_app_runner.py'
        assert command[2:] == [
            '--app-module',
            DummyTestHostApp.__module__,
            '--app-class',
            DummyTestHostApp.__name__,
            '--app-kwargs',
            '{"argument": 1}'
        ]

    def test_launch_invokes_popen_with_expected_kwargs(self, example_host, example_context):
        example_host.launch_app(
            DummyTestHostApp,
            example_context,
            argument=1
        )

        args, kwargs = example_host.mn_host.popen.call_args

        assert kwargs['env']['PYTHONPATH'] == str(
            Environment.get_environment().project_root
        )
        assert kwargs['cwd'] == example_context.experiment_root
        assert kwargs['stdout'].name == str(
            example_context.stdout_path / 'h1.out'
        )
        assert kwargs['stderr'].name == str(
            example_context.stdout_path / 'h1.err'
        )

    def test_host_can_launch_another_app_after_stop(self, example_host, example_context):
        example_host.launch_app(DummyTestHostApp,
                                example_context,
                                argument=1)

        assert example_host.app.argument == 1

        example_host._stop()
        example_host.launch_app(DummyTestHostApp,
                                example_context,
                                argument=2)

        assert example_host.app.argument == 2

    # noinspection PyTypeChecker
    def test_launch_app_fails_if_an_application_is_already_running(self, example_host, example_context):
        example_host.launch_app(DummyTestHostApp, example_context)
        with pytest.raises(RuntimeError, match='Host h1 already has an application running'):
            example_host.launch_app(DummyTestHostApp, example_context)