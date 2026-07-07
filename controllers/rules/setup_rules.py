def install_send_everything_to_controller_rule(datapath):
    openflow_constants = datapath.ofproto
    openflow_parser = datapath.ofproto_parser

    # Minima prioridad - coincidir con tod0
    match = openflow_parser.OFPMatch()

    actions = [
        openflow_parser.OFPActionOutput(
            openflow_constants.OFPP_CONTROLLER,
            openflow_constants.OFPCML_NO_BUFFER
        )
    ]

    inst = [
        openflow_parser.OFPInstructionActions(
            openflow_constants.OFPIT_APPLY_ACTIONS, actions
        )
    ]

    mod = openflow_parser.OFPFlowMod(
        datapath=datapath,
        priority=0,
        match=match,
        instructions=inst
    )

    datapath.send_msg(mod)


def install_discard_ipv6_traffic_rule(datapath):
    openflow_parser = datapath.ofproto_parser

    # Coincidir los paquetes de IPv6
    match_ipv6 = openflow_parser.OFPMatch(
        eth_type=0x86dd
    )

    inst = []

    # Con alta prioridad, no hacemos nada con los paquetes ipv6
    mod = openflow_parser.OFPFlowMod(
        datapath=datapath,
        priority=10,
        match=match_ipv6,
        instructions=inst
    )

    datapath.send_msg(mod)
