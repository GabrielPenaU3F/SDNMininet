from pathlib import Path

Path('measurements').mkdir(exist_ok=True)
Path('measurements/host_program.txt').write_text('ok')
