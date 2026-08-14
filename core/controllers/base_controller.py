import json
import os
import socket
import time
import logging
from abc import ABC
from pathlib import Path
from typing import Any

from ryu.base import app_manager
from ryu.controller import ofp_event

from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet
from ryu.ofproto import ofproto_v1_3

from core.controllers.rules.packetin_rules import install_port_to_mac_rule
from core.controllers.rules.setup_rules import install_send_everything_to_controller_rule, install_discard_ipv6_traffic_rule
from core.config.environment import Environment


class BaseController(app_manager.RyuApp, ABC):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_logging()
        self.mac_tables = {}
        self.switches = {}
        self.current_poll_id = 0
        self.switch_poll = {}
        self._load_config()
        self.t0 = time.monotonic()

    def start(self):
        self.logger.info('Launching Ryu')
        super().start()
        self._signal_startup_complete()
        self.logger.info('Ryu: startup complete')

    # ===== Event Handlers

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.logger.info(
            f'Switch online: {datapath.id}'
        )

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
        msg = ev.msg
        datapath = msg.datapath

        self.mac_tables[datapath.id][eth.src] = in_port

        if eth.dst not in self.mac_tables[datapath.id].keys():
            out_port = datapath.ofproto.OFPP_FLOOD
        else:
            out_port = self.mac_tables[datapath.id][eth.dst]
            install_port_to_mac_rule(datapath, eth.dst, out_port)
            self.logger.info(f'Forwarding packet to {eth.dst}')
            self.logger.info(
                f'Installing rule: dst={eth.dst}, out_port={out_port}'
            )

        self.forward_packet(datapath, msg, out_port)

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
        config_file = Path(os.environ['EXPERIMENT_CFG'])
        with config_file.open() as f:
            cfg = json.load(f)

        self.sampling_interval = cfg['sampling_interval']
        self.seed = cfg['seed']
        self.experiment_root = Path(cfg['experiment_root'])

    def _setup_logging(self):

        # Clean old logs
        self.logfile.unlink(missing_ok=True)

        # Remove old handlers
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            handler.close()

        # Add file handler - log to file
        file_handler = logging.FileHandler(self.logfile)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    @property
    def logfile(self):
        return Path('logs/controller.log')