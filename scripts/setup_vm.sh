#!/bin/bash
# Setup script for Ubuntu VM (Section VI-A, Table III)
# Installs Docker, Falco (modern eBPF), Python venv, and copies config files.

set -e

echo "[*] Updating package list..."
sudo apt-get update -y
sudo apt-get install -y curl gnupg2 software-properties-common python3 python3-venv

echo "[*] Installing Docker Engine..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

echo "[*] Installing Falco 0.45.2 (modern eBPF)..."
if ! command -v falco &> /dev/null; then
    curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | sudo gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" | sudo tee -a /etc/apt/sources.list.d/falcosecurity.list
    sudo apt-get update -y
    sudo apt-get install -y falco
fi

echo "[*] Setting up Falco configuration and custom rules..."
sudo mkdir -p /etc/falco/rules.d /var/log/falco
sudo cp config/falco-custom-rules.yaml /etc/falco/rules.d/
if [ -f config/falco.yaml ]; then
    sudo cp config/falco.yaml /etc/falco/falco.yaml
fi

echo "[*] Starting Falco service with modern eBPF driver..."
sudo systemctl restart falco || echo "[!] Falco service restart: please verify kernel headers and eBPF support."

echo "[*] Setting up Python virtual environment for KubAnomaly Agent..."
python3 -m venv ~/kubanomaly-venv
source ~/kubanomaly-venv/bin/activate
pip install requests

echo "[*] Setup complete! You can now run:"
echo "    python agent/kubanomaly_agent.py --log /var/log/falco/events.json --center http://<HOST_IP>:8003"
echo "    python agent/kubanomaly_hardware.py --center http://<HOST_IP>:8003"
