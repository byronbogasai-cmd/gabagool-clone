#!/bin/bash
# Google Cloud Free Tier Setup Script
# Run this on a fresh e2-micro instance (Debian/Ubuntu)

set -e

echo "=== Gabagool Clone — Server Setup ==="

# Update system
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Python 3.11+
sudo apt-get install -y python3 python3-pip python3-venv git screen

# Clone repo
git clone https://github.com/byronbogasai-cmd/gabagool-clone.git
cd gabagool-clone

# Create virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
echo ""
echo "=== ACTION REQUIRED ==="
echo "Edit .env with your Polymarket API credentials:"
echo "  nano .env"
echo ""
echo "Then start the bot:"
echo "  screen -S bot"
echo "  source venv/bin/activate"
echo "  python main.py --capital 5.00"
echo "  (Ctrl+A then D to detach — bot keeps running)"
echo ""
echo "Check bot anytime:"
echo "  screen -r bot"
echo "  python main.py --summary"
