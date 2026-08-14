from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER

from core.controllers.monitor_controller import MonitorController


class DebugController(MonitorController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.write_config()

    @set_ev_cls(
        ofp_event.EventOFPFlowStatsReply,
        MAIN_DISPATCHER
    )
    def flow_stats_reply_handler(self, ev):
        for stat in ev.msg.body:
            self.logger.info(stat)

    def write_config(self):
        with open(self.logfile, 'w') as f:
            f.write(f'SI={str(self.sampling_interval)}\n')
            f.flush()