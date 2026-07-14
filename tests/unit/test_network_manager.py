from unittest.mock import Mock

import pytest
import infrastructure.network_manager as network_module

from infrastructure.network_manager import NetworkManager
from tests.dummies.dummy_topology import DummyTopology


@pytest.fixture
def network_manager():
    return NetworkManager(DummyTopology)

@pytest.fixture()
def make_mininet_patch(monkeypatch):
    def _make(return_value):
        monkeypatch.setattr(
            network_module,
            "Mininet",
            Mock(return_value=return_value)
        )
    return _make


class TestBuildNetwork:

    def test_build_network_creates_net(self, monkeypatch, network_manager, make_mininet_patch):
        net_mock = Mock()
        make_mininet_patch(net_mock)
        net = network_manager.build_network()
        assert network_manager._net is net

    def test_build_network_uses_given_topology(self, monkeypatch, network_manager, make_mininet_patch):
        topo = Mock()
        net_mock = Mock()
        make_mininet_patch(net_mock)

        monkeypatch.setattr(
            network_manager,
            "topology_cls",
            Mock(return_value=topo)
        )

        network_manager.build_network()

        network_module.Mininet.assert_called_once_with(
            topo=topo,
            controller=None,
            autoSetMacs=False
        )

    def test_build_network_adds_remote_controller(self, monkeypatch, network_manager, make_mininet_patch):
        mock_net = Mock()
        make_mininet_patch(mock_net)
        net = network_manager.build_network()

        net.addController.assert_called_once_with(
            "c0",
            controller=network_module.RemoteController,
            ip="127.0.0.1",
            port=6633
        )

    def test_build_network_accepts_custom_controller_address(self, monkeypatch, network_manager, make_mininet_patch):
        mock_net = Mock()
        make_mininet_patch(mock_net)

        net = network_manager.build_network(
            controller_ip="10.0.0.5",
            controller_port=9999
        )

        net.addController.assert_called_once_with(
            "c0",
            controller=network_module.RemoteController,
            ip="10.0.0.5",
            port=9999
        )


class TestStart:

    def test_start_starts_network(self, network_manager):
        network_manager._net = Mock()
        network_manager.start()
        network_manager._net.start.assert_called_once()

class TestStop:

    def test_stop_stops_network(self, network_manager):
        network_manager._net = Mock()
        network_manager.stop()
        network_manager._net.stop.assert_called_once()

    def test_stop_does_nothing_if_network_was_not_created(self, network_manager):
        network_manager.stop()
