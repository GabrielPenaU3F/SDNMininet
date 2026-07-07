from typing import Any

from ryu.base import app_manager
from ryu.controller import ofp_event

from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet
from ryu.ofproto import ofproto_v1_3

from controllers.rules.setup_rules import install_send_everything_to_controller_rule, install_discard_ipv6_traffic_rule
from controllers.rules.packetin_rules import install_port_to_mac_rule


class TestController(app_manager.RyuApp):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info("Levantando Ryu")
        self.mac_tables = {}

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.logger.info(
            f"Switch conectado: {datapath.id}"
        )
        # self.logger.info( f"Versión {datapath.ofproto.OFP_VERSION}")

        switch_id = datapath.id
        self.mac_tables[switch_id] = {} # Crear tabla vacía para el switch

        install_send_everything_to_controller_rule(datapath)
        install_discard_ipv6_traffic_rule(datapath)


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

        self.mac_tables[datapath.id][eth.src] = in_port

        if eth.dst not in self.mac_tables[datapath.id].keys():
            out_port = datapath.ofproto.OFPP_FLOOD
            self.logger.info("Haciendo flood")
        else:
            out_port = self.mac_tables[datapath.id][eth.dst]
            self.logger.info(f"Redirigiendo paquete a {eth.dst}")
            install_port_to_mac_rule(datapath, eth.dst, out_port)
            self.logger.info(f"Instalando regla")

        self.forward_packet(datapath, msg, out_port)


    def forward_packet(self, datapath, msg, port) -> Any:
        openflow_parser = datapath.ofproto_parser

        actions = [
            openflow_parser.OFPActionOutput(
                port
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
