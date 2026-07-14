import pytest

from infrastructure.network_manager import NetworkManager
from topologies.simple_topology import SimpleTopology

@pytest.fixture
def network_manager_with_simple_topo():
    manager = NetworkManager(SimpleTopology)
    yield manager
    manager.stop()

class TestNetworkManagerIntegration:

    def test_can_build_start_and_stop_network(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()

        assert manager.net is not None
        manager.start()

        h1 = manager.net.get("h1")
        h2 = manager.net.get("h2")
        s1 = manager.net.get("s1")
        assert h1 is not None
        assert h2 is not None
        assert s1 is not None

    def test_network_hosts_are_running(self, network_manager_with_simple_topo):
        manager = network_manager_with_simple_topo
        manager.build_network()
        manager.start()

        h = manager.net.get("h1")
        assert h.cmd("echo hello").strip() == "hello"
