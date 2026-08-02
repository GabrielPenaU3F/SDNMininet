import time

from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER

from controllers.base_controller import BaseController


class DebugController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_rx = {}
        self.last_tx = {}

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

            print(
                f'Poll {poll_id} '
                f'Port {port} '
                f'RX={rx_packets} '
                f'LAST={self.last_rx[port]} '
                f'DELTA={rx_packets - self.last_rx[port]}'
            )
            # print(f'Poll ID: {poll_id} -- Time: {time.monotonic() - self.t0:.6f} -- Port: {port}'
            #       f' -- RX Packets: {rx_packets - self.last_rx.get(port)}'
            #       f' -- TX Packets: {tx_packets - self.last_tx.get(port)}')
            self.last_rx[port] = rx_packets
            self.last_tx[port] = tx_packets
