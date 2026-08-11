from core.controllers.monitor_controller import MonitorController


class DebugController(MonitorController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_file = self._open_measurement_file()
        self.write_config()

    def _open_measurement_file(self):
        f = open(self.experiment_root / 'measurements' / 'test_file', 'w', newline='')
        f.write('Debugging...\n')
        f.flush()
        return f

    def write_config(self):
        self._test_file.write(f'SI={str(self.sampling_interval)}\n')
        self._test_file.flush()