from extras.constants import ETH_IPV6


def install_send_everything_to_controller_rule(datapath):
    openflow_constants = datapath.ofproto
    openflow_parser = datapath.ofproto_parser

    # Minimum priority - match everything
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

    # Match IPv6 packets
    match_ipv6 = openflow_parser.OFPMatch(
        eth_type=ETH_IPV6
    )

    inst = []

    # Drop IPv6 packets with high priority
    mod = openflow_parser.OFPFlowMod(
        datapath=datapath,
        priority=10,
        match=match_ipv6,
        instructions=inst
    )

    datapath.send_msg(mod)
