#!/bin/bash

# Any test involving Mininet needs to be run with root privileges

cd ~/SDN
sudo .venv/bin/python -m pytest tests/integration "$@"