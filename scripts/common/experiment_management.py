from scripts.common.controller_management import stop_controller, start_controller
from scripts.common.network_management import build_network


def begin_experiment(controller_path, topology_cls,
                     controller_ip='127.0.0.1', controller_port=6633):
    controller = start_controller(controller_path, controller_ip=controller_ip, controller_port=controller_port)
    net = build_network(topology_cls, controller_ip=controller_ip, controller_port=controller_port)
    net.start()
    return net, controller

def shutdown_experiment(net, controller):
    net.stop()
    stop_controller(controller)
