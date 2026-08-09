import subprocess

import pytest
from mininet.net import Mininet
from mininet.node import OVSSwitch

from core.network_manager import NetworkManager
from errors import NetworkError
from hosts.host import Host
from topologies.simple_topology import SimpleTopology

@pytest.fixture
def network_manager_with_simple_topo():
    manager = NetworkManager(SimpleTopology)
    yield manager
    manager.destroy_network()

class TestNetworkManagerIntegration:

    def test_manager_builds_real_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()

        h1 = manager.host('h1')
        h2 = manager.host('h2')
        s1 = manager.switch('s1')

        assert h1 is not None
        assert isinstance(h1, Host)
        assert h2 is not None
        assert isinstance(h2, Host)
        assert s1 is not None
        assert isinstance(s1, OVSSwitch) # Eventually change if we wrap switches too

        assert manager.net is not None
        assert isinstance(manager.net, Mininet)

    # This should be done without any error
    def test_destroy_removes_built_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.destroy_network()
        manager.build_network()

    def test_manager_starts_and_stops_real_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start_network()
        assert manager.network_online
        manager.stop_network()
        assert not manager.network_online

    def test_network_hosts_are_running_when_network_starts(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start_network()

        h = manager.host('h1')
        assert h.cmd('echo hello').strip() == 'hello'

    def test_network_hosts_are_not_running_when_network_has_not_started(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()

        h = manager.host('h1')
        with pytest.raises(NetworkError, match='Host h1 is not active'):
            h.cmd('echo hello')

    def test_network_hosts_are_not_running_when_network_stops(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start_network()
        manager.stop_network()

        h = manager.host('h1')
        with pytest.raises(NetworkError, match='Host h1 is not active'):
            h.cmd('echo hello')

