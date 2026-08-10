from pathlib import Path

import pytest

from unittest.mock import Mock

from core.config.environment import Environment
from hosts.host import Host
from hosts.host_app import HostAppContext
from tests.utilities.dummy_host_apps import DummyTestHostApp


@pytest.fixture
def dummy_mn_host():
    mn_host = Mock()
    mn_host.name = 'h1'
    mn_host.IP.return_value = '127.0.0.1'
    process = object()
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


class TestLaunchApp:

    def test_launch_stores_app_and_process(self, example_host, example_context):
        app = DummyTestHostApp()
        example_host.launch_app(app, example_context)

        assert example_host.app is app
        assert example_host.process is example_host.mn_host.popen.return_value

    def test_launch_invokes_popen_with_expected_command(self, example_host, example_context):
        app = DummyTestHostApp()
        example_host.launch_app(
            app,
            example_context,
            rate=100,
            duration=60
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
            '{"rate": 100, "duration": 60}'
        ]

    def test_launch_invokes_popen_with_expected_kwargs(self, example_host, example_context):
        app = DummyTestHostApp()
        example_host.launch_app(
            app,
            example_context,
            rate=100,
            duration=60
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

    # noinspection PyTypeChecker
    def test_launch_app_fails_if_an_application_is_already_running(self, example_host, example_context):
        example_host.launch_app(DummyTestHostApp, example_context)
        with pytest.raises(RuntimeError, match='Host h1 already has an application running'):
            example_host.launch_app(DummyTestHostApp, example_context)