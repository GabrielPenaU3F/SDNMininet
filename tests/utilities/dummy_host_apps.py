from pathlib import Path

from hosts.host_app import HostApp


class DummyTestHostApp(HostApp):

    def __init__(self, argument=0):
        self.argument = argument

    def run(self, **kwargs):
        print(f'Running host app: {self.argument}')


class WriteFileHostApp(HostApp):

    @staticmethod
    def run(**kwargs):
        Path('measurements').mkdir(exist_ok=True)
        Path('measurements/host_program.txt').write_text('ok')