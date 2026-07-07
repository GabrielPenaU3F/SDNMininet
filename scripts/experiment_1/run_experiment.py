import os
import subprocess
import time

import numpy as np

from pathlib import Path
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.clean import cleanup

from topologies.test_topologies import AwadDDoSTopology

PROJECT_ROOT = Path(__file__).resolve().parents[2]
env = os.environ.copy()
env["PYTHONPATH"] = str(PROJECT_ROOT)

cleanup()

ryu = subprocess.Popen(
    [
        "/home/sskies/SDN/.venv/bin/ryu-manager",
        "controllers/first_measurement_controller/controller.py"
    ], env=env
)
time.sleep(2)

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
ryu.terminate()
ryu.wait()
