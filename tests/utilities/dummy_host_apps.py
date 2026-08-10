from pathlib import Path

from hosts.host_app import HostApp


class DummyTestHostApp(HostApp):

    @staticmethod
    def run(**kwargs):
        print('Running host app')

class WriteFileHostApp(HostApp):

    @staticmethod
    def run(**kwargs):
        Path('measurements').mkdir(exist_ok=True)
        Path('measurements/host_program.txt').write_text('ok')