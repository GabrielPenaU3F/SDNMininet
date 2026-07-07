import numpy as np

from mininet.net import Mininet
from mininet.node import RemoteController

from scripts.common.controller_management import stop_controller, start_controller
from scripts.common.environment import Environment
from topologies.test_topologies import AwadDDoSTopology

env = Environment.get_environment()
ryu = start_controller("controllers/first_measurement_controller/controller.py")

topo = AwadDDoSTopology()

net = Mininet(
    topo=topo,
    controller=None,
    autoSetMacs=False
)

net.addController(
    "c0",
    controller=RemoteController,
    ip="127.0.0.1",
    port=6633
)

net.start()

h1 = net["h1"]
h2 = net["h2"]

basepath = '/home/sskies/SDN/scripts/experiment_1'

rate_1, rate_2 = np.random.uniform(0, 10, 2)

h1.popen([
    "/home/sskies/SDN/.venv/bin/python",
    "/home/sskies/SDN/scripts/experiment_1/host_program.py",
    "--dst_ip", "10.0.0.2",
    "--port", "100",
    "--rate", f'{rate_1}'
],
env=env)

h2.popen([
    "/home/sskies/SDN/.venv/bin/python",
    "/home/sskies/SDN/scripts/experiment_1/host_program.py",
    "--dst_ip", "10.0.0.1",
    "--port", "100",
    "--rate", f'{rate_2}'
],
env=env)

input("Presione ENTER para finalizar...")
net.stop()
stop_controller(ryu)
