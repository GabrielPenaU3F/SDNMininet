from pathlib import Path


class WriteFileTestApp:

    @staticmethod
    def run():
        Path('measurements').mkdir(exist_ok=True)
        Path('measurements/host_program.txt').write_text('ok')