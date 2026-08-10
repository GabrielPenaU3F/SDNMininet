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


def add_mock_mininet_hosts(net_mock):
    mn_h1 = Mock(spec=MininetHost)
    mn_h1.name = 'h1'

    mn_h2 = Mock(spec=MininetHost)
    mn_h2.name = 'h2'

    net_mock.nameToNode = {
        'h1': mn_h1,
        'h2': mn_h2,
    }
    return net_mock, mn_h1, mn_h2


class TestNetworkManagerGeneral:

    def test_manager_wraps_each_host_in_the_network(self, network_manager, make_mininet_patch, net_mock):
        net_mock, mn_h1, mn_h2 = add_mock_mininet_hosts(net_mock)
        make_mininet_patch(net_mock)
        network_manager.net = net_mock
        network_manager._wrap_hosts()

        assert isinstance(network_manager.host('h1'), Host)
        assert isinstance(network_manager.host('h2'), Host)
        assert network_manager.host('h1').mn_host is mn_h1
        assert network_manager.host('h2').mn_host is mn_h2


class TestBuildNetwork:

    def test_build_network_creates_net(self, network_manager, net_mock):
        net = network_manager._build_network()
        assert net is net_mock

    # noinspection PyUnresolvedReferences
    def test_build_network_uses_given_topology(self, monkeypatch, network_manager, net_mock):
        topo = Mock()

        monkeypatch.setattr(
            network_manager,
            'topology_cls',
            Mock(return_value=topo)
        )

        network_manager._build_network()

        network_module.Mininet.assert_called_once_with(
            topo=topo,
            controller=None,
            autoSetMacs=False
        )

    def test_build_network_adds_remote_controller(self, network_manager, net_mock):
        net = network_manager._build_network()

        net.addController.assert_called_once_with(
            'c0',
            controller=network_module.RemoteController,
            ip='127.0.0.1',
            port=6633
        )

    def test_build_network_accepts_custom_controller_address(self, network_manager, net_mock):

        net = network_manager._build_network(
            controller_ip='10.0.0.5',
            controller_port=9999
        )

        net.addController.assert_called_once_with(
            'c0',
            controller=network_module.RemoteController,
            ip='10.0.0.5',
            port=9999
        )

class TestDeployNetwork:

    def test_start_starts_network(self, network_manager, net_mock):
        network_manager.net = net_mock
        network_manager.deploy_network()

        net_mock.start.assert_called_once()
        assert network_manager.network_online


class TestDestroy:

    def test_destroy_stops_mininet_network(self, network_manager):
        net = Mock()
        network_manager.net = net
        network_manager.destroy_network()
        assert network_manager._hosts == {}
        net.stop.assert_called_once()
        assert network_manager.net is None

    def test_destroy_stops_hosts_before_destroying_network(self, network_manager):
        net = Mock()
        network_manager.net = net

        h1 = Mock()
        h2 = Mock()
        network_manager._hosts = {'h1': h1, 'h2': h2}

        network_manager.destroy_network()

        h1._stop.assert_called_once()
        h2._stop.assert_called_once()
