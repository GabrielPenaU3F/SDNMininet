import time
from pathlib import Path

from hosts.host_apps.host_app import HostApp
from hosts.host_apps.minimal_apps import DeafSpeakerHostApp


class DummyTestHostApp(HostApp):

    def __init__(self, argument=0):
        super().__init__()
        self.argument = argument

    def run(self, **kwargs):
        print(f'Running host app: {self.argument}')


class WriteFileHostApp(HostApp):

    @staticmethod
    def run(**kwargs):
        Path('logs').mkdir(exist_ok=True)
        Path('logs/logfile.log').write_text('ok')


class FastDeafSpeakerTestHostApp(DeafSpeakerHostApp):

    @staticmethod
    def _idle_time():
        return 0.2