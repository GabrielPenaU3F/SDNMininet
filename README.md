# INSTALLATION

Do not install with root. Just run the following:
```bash
git clone https://github.com/GabrielPenaU3F/SDNMininet
cd SDNMininet
chmod +x scripts/install.sh
./scripts/install.sh
```

# HOW TO RUN
From a console on the project root directory run:

```bash
sudo .venv/bin/python \
    -m launch_experiment <experiment-name> --<option> <value>
```

## Currently supported options:
```bash
--duration <duration>
```

Experiments should be registered on experiment_register.py
