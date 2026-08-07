def install_port_to_mac_rule(datapath, dst_mac, out_port):
    openflow_constants = datapath.ofproto
    openflow_parser = datapath.ofproto_parser

    match = openflow_parser.OFPMatch(eth_dst=dst_mac)

    actions = [
        openflow_parser.OFPActionOutput(out_port)
    ]

    inst = [
        openflow_parser.OFPInstructionActions(
            openflow_constants.OFPIT_APPLY_ACTIONS, actions
        )
    ]

    mod = openflow_parser.OFPFlowMod(
        datapath=datapath,
        priority=2,
        match=match,
        instructions=inst,
        idle_timeout=30
    )

    datapath.send_msg(mod)