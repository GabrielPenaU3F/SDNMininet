import numpy as np


from scripts.common.environment import Environment
from scripts.common.experiment_management import shutdown_experiment, begin_experiment
from topologies.test_topologies import AwadDDoSTopology

env = Environment.get_environment()

net, ryu = begin_experiment(controller_path="controllers/first_measurement_controller/controller.py",
                            topology_cls=AwadDDoSTopology)

h1 = net["h1"]
h2 = net["h2"]

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

shutdown_experiment(net, ryu)
