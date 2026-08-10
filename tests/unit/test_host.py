import pytest

from unittest.mock import Mock

from hosts.host import Host

@pytest.fixture
def example_host():
    mn_host = Mock()
    mn_host.name = 'h1'
    mn_host.IP.return_value = '127.0.0.1'
    return Host(mn_host)

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
