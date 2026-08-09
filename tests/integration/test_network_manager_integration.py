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
    manager.stop()

class TestNetworkManagerIntegration:

    def test_manager_builds_real_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()

        assert manager.net is not None
        assert isinstance(manager.net, Mininet)

    def test_manager_starts_real_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start()
        h1 = manager.host('h1')
        h2 = manager.host('h2')
        s1 = manager.switch('s1')

        assert h1 is not None
        assert isinstance(h1, Host)
        assert h2 is not None
        assert isinstance(h2, Host)
        assert s1 is not None
        assert isinstance(s1, OVSSwitch) # Eventually change if we wrap switches too

    def test_network_hosts_are_running(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start()

        h = manager.host('h1')
        assert h.cmd('echo hello').strip() == 'hello'

    # def test_manager_stops_real_network(self, network_manager_with_simple_topo):
    #     manager = NetworkManager(SimpleTopology)
    #     manager.build_network()
    #     manager.start()
    #
    #     h = manager.host('h1')
    #     manager.stop()
    #
    #     with pytest.raises(NetworkError):
    #         assert h.cmd('echo hello')
