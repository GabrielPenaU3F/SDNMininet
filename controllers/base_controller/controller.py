import csv
import os
import socket
import time
from typing import Any

from ryu.base import app_manager
from ryu.controller import ofp_event

from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib import hub
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet
from ryu.ofproto import ofproto_v1_3

from controllers.rules.packetin_rules import install_port_to_mac_rule
from controllers.rules.setup_rules import install_send_everything_to_controller_rule, install_discard_ipv6_traffic_rule
from config.environment import Environment


class BaseController(app_manager.RyuApp):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info('Launching Ryu')
        self.mac_tables = {}
        self.switches = {}

        self.csv_file = open(
            Environment.get_environment().traffic_stats_file,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)
        self._setup_csv_header()

    def start(self):
        super().start()
        self._set_up_monitor()
        self._signal_startup_complete()
        self.logger.info('Ryu: startup complete')

    def _set_up_monitor(self):
        self.monitor_thread = hub.spawn(self._monitor)  # Thread con tareas de monitoreo
        self.logger.info('Monitor online - receiving stats')

    # Event Handlers

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.logger.info(
            f'Switch online: {datapath.id}'
        )
        # self.logger.info( f"Versión {datapath.ofproto.OFP_VERSION}")

        switch_id = datapath.id
        self.switches[switch_id] = datapath # Guardamos el switch
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
            'In port = {in_port}, '
            'Source MAC = {eth.src}, '
            'Destination MAC = {eth.dst}, '
            'Ethernet type = {hex(eth.ethertype)}'
        )
        msg = ev.msg
        datapath = msg.datapath

        self.mac_tables[datapath.id][eth.src] = in_port

        if eth.dst not in self.mac_tables[datapath.id].keys():
            out_port = datapath.ofproto.OFPP_FLOOD
        else:
            out_port = self.mac_tables[datapath.id][eth.dst]
            self.logger.info(f'Forwarding packet to {eth.dst}')
            install_port_to_mac_rule(datapath, eth.dst, out_port)
            self.logger.info(f'Installing rule')

        self.forward_packet(datapath, msg, out_port)


    @set_ev_cls(
        ofp_event.EventOFPPortStatsReply,
        MAIN_DISPATCHER
    )
    def port_stats_reply_handler(self, ev):
        body = ev.msg.body
        switch_id = ev.msg.datapath.id
        for stat in body:
            if stat.port_no > 0xffffff00:
                continue

            self.csv_writer.writerow([
                time.time(),
                switch_id,
                stat.port_no,
                stat.rx_packets,
                stat.tx_packets,
                stat.rx_bytes,
                stat.tx_bytes
            ])

        self.csv_file.flush()

    # Metodos

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

    def request_port_stats(self, datapath):
        parser = datapath.ofproto_parser
        req = parser.OFPPortStatsRequest(datapath)
        datapath.send_msg(req)

    # Tarea periódica: cada 1 segundo pide estadísticas a todos los switches
    def _monitor(self):
        while True:
            for datapath in self.switches.values():
                self.request_port_stats(datapath)

            hub.sleep(1)

    def _setup_csv_header(self):
        self.csv_writer.writerow([
            "timestamp",
            "switch_id",
            "port_no",
            "rx_packets",
            "tx_packets",
            "rx_bytes",
            "tx_bytes"
        ])

    def _signal_startup_complete(self):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.settimeout(30)
        socket_path = os.path.join(Environment.get_environment().controller_ready_sock)
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        server.bind(socket_path)
        server.listen()

        try:
            conn, _ = server.accept()
            conn.sendall(b'READY')
            conn.close()

        except socket.timeout:
            self.logger.warning(
                'No network connected to Ryu'
            )

        finally:
            server.close()
            if os.path.exists(socket_path):
                os.unlink(socket_path)
