import numpy as np


from src.config.environment import Environment
from experiments.experiment_management import shutdown_experiment, begin_experiment
from infrastructure.host_program_launcher import launch_program
from topologies.test_topologies import AwadDDoSTopology

env = Environment.get_environment()

net, ryu = begin_experiment(controller_path="controllers/first_measurement_controller/controller.py",
                            topology_cls=AwadDDoSTopology)

h1 = net["h1"]
h2 = net["h2"]

rate_1, rate_2 = np.random.uniform(0, 10, 2)

launch_program(h1, '/experiments/experiment_1/host_program.py',
               dst_ip='10.0.0.2', port='100', rate=rate_1)
launch_program(h2, '/experiments/experiment_1/host_program.py',
               dst_ip='10.0.0.1', port='100', rate=rate_2)

input("Presione ENTER para finalizar...")

shutdown_experiment(net, ryu)
