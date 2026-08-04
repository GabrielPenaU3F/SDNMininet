import time

from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.lib.packet import ethernet
from ryu.lib.packet.packet import Packet

from controllers.base_controller import BaseController


class DebugController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_file = self._open_measurement_file()
        self.last_rx = {}
        self.last_tx = {}
        self.write_config()

    @staticmethod
    def _open_measurement_file():
        f = open('measurements/test_file', 'w', newline='')
        f.write('Debugging...\n')
        f.flush()
        return f


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
            port = stat.port_no
            rx_packets = stat.rx_packets
            tx_packets = stat.tx_packets
            if port not in self.last_rx.keys():
                self.last_rx[port] = rx_packets

            if port not in self.last_tx.keys():
                self.last_tx[port] = tx_packets

            print(f'Poll ID: {poll_id} -- Time: {time.monotonic() - self.t0:.6f} -- Port: {port}'
                  f' -- RX Packets: {rx_packets - self.last_rx.get(port)}'
                  f' -- TX Packets: {tx_packets - self.last_tx.get(port)}')
            self.last_rx[port] = rx_packets
            self.last_tx[port] = tx_packets

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

    def write_config(self):
        self._test_file.write(f'SI={str(self.sampling_interval)}\n')
        self._test_file.flush()
