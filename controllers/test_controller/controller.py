from ryu.base import app_manager
from ryu.controller import ofp_event

from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet
from ryu.ofproto import ofproto_v1_3


class TestController(app_manager.RyuApp):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info("Levantando Ryu")

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.logger.info(
            f"Switch conectado: {datapath.id}"
        )
        self.logger.info( f"Versión {datapath.ofproto.OFP_VERSION}")
        openflow_constants = datapath.ofproto
        openflow_parser = datapath.ofproto_parser

        # Maxima prioridad - coincidir con tod0
        match = openflow_parser.OFPMatch()

        #
        match_ipv6 = openflow_parser.OFPMatch(
            eth_type=0x86dd
        )

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


    @set_ev_cls(
        ofp_event.EventOFPPacketIn,
        MAIN_DISPATCHER
    )
    def packet_in_handler(self, ev):
        pkt = Packet(ev.msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        in_port = ev.msg.match['in_port']

        self.logger.info(
            f"Puerto de entrada={in_port}, "
            f"MAC origen={eth.src}, "
            f"MAC destino={eth.dst}, "
            f"Tipo Ethernet = {hex(eth.ethertype)}"
        )
        msg = ev.msg
        datapath = msg.datapath

        openflow_constants = datapath.ofproto
        openflow_parser = datapath.ofproto_parser

        actions = [
            openflow_parser.OFPActionOutput(
                openflow_constants.OFPP_FLOOD
            )
        ]

        out = openflow_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=msg.match['in_port'],
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)

        self.logger.info("Flooding packet")
