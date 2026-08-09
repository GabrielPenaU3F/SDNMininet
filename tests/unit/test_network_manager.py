from unittest.mock import Mock

import pytest
import core.network_manager as network_module

from core.network_manager import NetworkManager
from hosts.host import Host
from tests.dummies.dummy_topology import DummyTopology
from mininet.node import Host as MininetHost


@pytest.fixture
def network_manager(monkeypatch):
    manager = NetworkManager(DummyTopology)
    return manager

@pytest.fixture()
def make_mininet_patch(monkeypatch):
    def _make(return_value):
        monkeypatch.setattr(
            network_module,
            'Mininet',
            Mock(return_value=return_value)
        )
    return _make

@pytest.fixture()
def net_mock(make_mininet_patch):
    net_mock = Mock()
    net_mock.nameToNode = {}
    make_mininet_patch(net_mock)
    return net_mock


class TestBuildNetwork:

    def test_build_network_creates_net(self, network_manager, net_mock):
        net = network_manager.build_network()
        assert network_manager.net is net

    # noinspection PyUnresolvedReferences
    def test_build_network_uses_given_topology(self, monkeypatch, network_manager, net_mock):
        topo = Mock()

        monkeypatch.setattr(
            network_manager,
            'topology_cls',
            Mock(return_value=topo)
        )

        network_manager.build_network()

        network_module.Mininet.assert_called_once_with(
            topo=topo,
            controller=None,
            autoSetMacs=False
        )

    def test_build_network_adds_remote_controller(self, network_manager, net_mock):
        net = network_manager.build_network()

        net.addController.assert_called_once_with(
            'c0',
            controller=network_module.RemoteController,
            ip='127.0.0.1',
            port=6633
        )

    def test_build_network_accepts_custom_controller_address(self, network_manager, net_mock):

        net = network_manager.build_network(
            controller_ip='10.0.0.5',
            controller_port=9999
        )

        net.addController.assert_called_once_with(
            'c0',
            controller=network_module.RemoteController,
            ip='10.0.0.5',
            port=9999
        )


class TestManagerWrapsHosts:

    def test_manager_wraps_each_host_in_the_network(self, network_manager, make_mininet_patch):
        net_mock = Mock()
        mn_h1 = Mock(spec=MininetHost)
        mn_h1.name = 'h1'

        mn_h2 = Mock(spec=MininetHost)
        mn_h2.name = 'h2'

        net_mock.nameToNode = {
            'h1': mn_h1,
            'h2': mn_h2,
        }

        make_mininet_patch(net_mock)
        network_manager.build_network()

        assert isinstance(network_manager.host('h1'), Host)
        assert isinstance(network_manager.host('h2'), Host)
        assert network_manager.host('h1').mn_host is mn_h1
        assert network_manager.host('h2').mn_host is mn_h2


class TestStart:

    def test_start_starts_network(self, network_manager):
        network_manager.net = Mock()
        network_manager.start_network()
        network_manager.net.start.assert_called_once()
        assert network_manager.network_online

    def test_start_does_nothing_if_network_is_already_running(self, network_manager):
        network_manager.net = Mock()
        network_manager._running = True
        network_manager.start_network()
        network_manager.net.start.assert_not_called()

    def test_network_manager_starts_hosts(self, network_manager):
        network_manager.net = Mock()
        h1 = Mock()
        h2 = Mock()
        network_manager._hosts = {'h1': h1, 'h2': h2}
        network_manager.start_network()
        network_manager.net.start.assert_called_once()
        h1._start.assert_called_once()
        h2._start.assert_called_once()

class TestStop:

    def test_stop_stops_network(self, network_manager):
        network_manager.net = Mock()
        network_manager._running = True
        network_manager.stop_network()
        assert network_manager._running is False

    def test_stop_does_nothing_if_network_was_not_created(self, network_manager):
        network_manager.stop_network()

    def test_stop_does_nothing_if_network_is_not_running(self, network_manager):
        network_manager.net = Mock()
        network_manager._running = False
        network_manager.stop_network()
        network_manager.net.stop.assert_not_called()

    def test_stop_stops_hosts(self, network_manager):
        network_manager.net = Mock()
        network_manager._running = True

        h1 = Mock()
        h2 = Mock()
        network_manager._hosts = {'h1': h1, 'h2': h2}

        network_manager.stop_network()

        h1._stop.assert_called_once()
        h2._stop.assert_called_once()
        assert not network_manager.network_online

    def test_stop_does_not_destroy_network_infrastructure(self, network_manager):
        network_manager.net = Mock()
        network_manager._running = True
        network_manager.stop_network()
        network_manager.net.stop.assert_not_called()
        assert network_manager.net is not None

class TestDestroy:

    def test_destroy_stops_mininet_network(self, network_manager):
        net = Mock()
        network_manager.net = net
        network_manager.destroy_network()
        net.stop.assert_called_once()
        assert network_manager.net is None

    def test_destroy_stops_hosts_before_destroying_network(self, network_manager):
        net = Mock()
        network_manager.net = net
        network_manager.start_network()

        h1 = Mock()
        h2 = Mock()
        network_manager._hosts = {'h1': h1, 'h2': h2}

        network_manager.destroy_network()

        h1._stop.assert_called_once()
        h2._stop.assert_called_once()
        net.stop.assert_called_once()
        assert not network_manager.network_online
        assert network_manager._hosts == {}
        assert network_manager.net is None
