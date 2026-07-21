#!/usr/bin/env bash

# Any test involving Mininet needs to be run with root privileges


set -e

cd ~/SDN

echo "Cleaning Mininet..."
sudo mn -c >/dev/null 2>&1 || true

echo "Stopping old Ryu processes..."
sudo pkill -f ryu-manager >/dev/null 2>&1 || true

echo "Removing stale Unix socket..."
sudo rm -f temp/ryu_ready.sock

echo "Running integration tests..."
sudo .venv/bin/python -m pytest tests/integration "$@"