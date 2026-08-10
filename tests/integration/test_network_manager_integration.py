import pytest
from mininet.net import Mininet
from mininet.node import Host as MininetHost
from mininet.node import OVSSwitch

from core.network_manager import NetworkManager
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
        manager.deploy_network()

        h1 = manager.host('h1')
        h2 = manager.host('h2')
        s1 = manager.switch('s1')

        assert isinstance(h1, Host)
        assert isinstance(h1.mn_host, MininetHost)
        assert isinstance(h2, Host)
        assert isinstance(h2.mn_host, MininetHost)
        assert isinstance(s1, OVSSwitch) # Eventually change if we wrap switches too

        assert manager.net is not None
        assert isinstance(manager.net, Mininet)

    # This should be done without any error
    def test_destroy_removes_built_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.deploy_network()
        manager.destroy_network()
        manager.deploy_network()

    def test_network_hosts_are_running_when_network_starts(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.deploy_network()

        h = manager.host('h1')
        assert h.cmd('echo hello').strip() == 'hello'

    def test_destroy_removes_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.deploy_network()
        manager.destroy_network()

        assert manager.net is None
        assert manager._hosts == {}
