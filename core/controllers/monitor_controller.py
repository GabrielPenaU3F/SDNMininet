import time

from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.lib import hub
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet

from core.controllers.base_controller import BaseController

'''
MonitorController makes polls every sampling_interval seconds
A poll is a round of solicitudes, emitted by the controller. 
Each answer is an independent observation, uniquely identified by the triplet
(poll_id, switch_id, port_no), paired with its reception time.
'''

class MonitorController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_up_monitor()
        self.current_poll_id = 0
        self.last_rx = {}
        self.last_tx = {}

    def _set_up_monitor(self):
        self.monitor_thread = hub.spawn(self._monitor)
        self.logger.info('Monitor online - receiving stats')

    # Ask for stats
    def _monitor(self):
        while True:
            self.current_poll_id += 1
            for datapath in self.switches.values():
                self.request_port_stats(datapath)

            hub.sleep(self.sampling_interval)

    @staticmethod
    def request_port_stats(datapath):
        parser = datapath.ofproto_parser
        req = parser.OFPPortStatsRequest(datapath)
        datapath.send_msg(req)


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

            poll_id = self.current_poll_id
            port = stat.port_no
            rx_packets = stat.rx_packets
            tx_packets = stat.tx_packets
            key = (switch_id, port)

            # Defaults to current packets if its the first poll
            previous_rx = self.last_rx.get(key, rx_packets)
            previous_tx = self.last_tx.get(key, tx_packets)

            self.logger.info(f'Poll ID: {poll_id} -- Time: {time.monotonic() - self.t0:.6f} -- Port: {port}'
                  f' -- RX Packets: {rx_packets - previous_rx}'
                  f' -- TX Packets: {tx_packets - previous_tx}')

            self.last_rx[key] = rx_packets
            self.last_tx[key] = tx_packets

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
        super().packet_in_handler(ev)
