import csv
import json
import os
import socket
import time
from pathlib import Path
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
        self.current_poll_id = 0
        self.switch_poll = {}
        # self.sampling_interval = float(os.getenv('SAMPLING_INTERVAL', '1.0'))
        self._traffic_stats_csv = self._open_traffic_stats_file()
        self.csv_writer = csv.writer(self._traffic_stats_csv)

        self._load_config()
        self._setup_csv_header()

    @staticmethod
    def _open_traffic_stats_file():
        return open(
            'measurements/traffic_stats.csv',
            'w',
            newline=''
        )

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
        self.switches[switch_id] = datapath # Record switch
        self.mac_tables[switch_id] = {} # Empty table for the switch

        # Install necessary rules
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
            f'In port = {in_port}, '
            f'Source MAC = {eth.src}, '
            f'Destination MAC = {eth.dst}, '
            f'Ethernet type = {hex(eth.ethertype)}'
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

            poll_id = self.switch_poll[switch_id]
            self.csv_writer.writerow([
                poll_id,
                time.time(),
                switch_id,
                stat.port_no,
                stat.rx_packets,
                # stat.tx_packets,
                stat.rx_bytes,
                # stat.tx_bytes
            ])

        self._traffic_stats_csv.flush()

    # Methods

    @staticmethod
    def forward_packet(datapath, msg, port) -> Any:
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

    @staticmethod
    def request_port_stats(datapath):
        parser = datapath.ofproto_parser
        req = parser.OFPPortStatsRequest(datapath)
        datapath.send_msg(req)

    # Ask for stats
    def _monitor(self):
        while True:
            self.current_poll_id += 1
            for datapath in self.switches.values():
                self.switch_poll[datapath.id] = self.current_poll_id
                self.request_port_stats(datapath)

            hub.sleep(self.sampling_interval)

    def _setup_csv_header(self):
        self.csv_writer.writerow([
            'poll_id',
            'timestamp',
            'switch_id',
            'port_no',
            'rx_packets',
            # "tx_packets",
            'rx_bytes',
            # "tx_bytes"
        ])

    def _signal_startup_complete(self):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.settimeout(30)
        socket_path = Environment.get_environment().controller_ready_sock
        self._unlink_socket(socket_path)
        server.bind(str(socket_path))
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
            self._unlink_socket(socket_path)

    @staticmethod
    def _unlink_socket(socket_path):
        if socket_path.exists():
            socket_path.unlink()

    def _load_config(self):
        experiment_name = Path.cwd().name
        config_file = Environment.get_environment().temp_path / f'{experiment_name}_cfg.json'
        with config_file.open() as f:
            cfg = json.load(f)

        self.sampling_interval = cfg['sampling_interval']
        self.seed = cfg['seed']
