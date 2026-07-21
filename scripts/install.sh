set -euo pipefail

echo "========================================="
echo " SDN Mininet Installer"
echo "========================================="
echo

echo "[0/5] Checking operating system..."

if [[ ! -f /etc/os-release ]]; then
    echo "Unable to identify the operating system."
    exit 1
fi

source /etc/os-release

echo "Detected: $PRETTY_NAME"
echo

if [[ "$ID" != "ubuntu" ]]; then
    echo "ERROR: This installer only supports Ubuntu."
    echo "Detected distribution: $PRETTY_NAME"
    exit 1
fi

echo "This installer supports Ubuntu systems."
echo "This project was developed and tested on Ubuntu 25.04 LTS."
echo "Other Ubuntu versions may work but are not officially supported."
echo

echo "[0/5] Updating..."
sudo apt update
echo

echo "Beginning installation..."
echo

echo "[1/5] Installing Mininet..."
sudo apt install -y git curl mininet
echo "Done"
echo

echo "[2/5] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
echo "Done"
echo

echo "[3/5] Installing Python 3.8..."
uv python install 3.8
echo "Done"
echo

echo "[4/5] Setting up environment..."
uv venv --python 3.8
source .venv/bin/activate
echo "Done"
echo

echo "[5/5] Resolving dependencies..."
uv pip install -e .
echo "Done"
echo

echo "Installation complete"