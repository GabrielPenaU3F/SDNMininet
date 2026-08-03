import csv
import time

from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER

from controllers.base_controller import BaseController


class Experiment1Controller(BaseController):

    def __init__(self):
        super().__init__()

        # Stats CSV
        self._traffic_stats_csv = self._open_traffic_stats_file()
        self.csv_writer = csv.writer(self._traffic_stats_csv)
        self._setup_csv_header()

    @staticmethod
    def _open_traffic_stats_file():
        return open(
            'measurements/traffic_stats.csv',
            'w',
            newline=''
        )

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
                f'{time.monotonic() - self.t0:.6f}',
                switch_id,
                stat.port_no,
                stat.rx_packets,
                # stat.tx_packets,
                stat.rx_bytes,
                # stat.tx_bytes
            ])

        self._traffic_stats_csv.flush()