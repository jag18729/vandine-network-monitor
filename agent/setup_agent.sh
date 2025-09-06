#!/bin/bash

echo "==============================================="
echo "Network Agent Setup Script"
echo "==============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "Checking Python installation..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
    echo -e "✓ Python $PYTHON_VERSION found"
else
    echo -e "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo -e "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "✓ Virtual environment created"
else
    echo -e "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo -e "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "Upgrading pip..."
pip install --upgrade pip wheel setuptools

# Install requirements
echo -e "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "✓ Requirements installed"
else
    echo -e "✗ requirements.txt not found"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "Creating .env file..."
    cat > .env << 'ENVFILE'
# Cloudflare Configuration
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ZONE_ID=your_zone_id_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=jag18729/vandine-network-monitor

# Agent Configuration
AGENT_MODE=development
AGENT_PORT=8000
AGENT_HOST=0.0.0.0

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Alerts (optional)
SLACK_WEBHOOK=
DISCORD_WEBHOOK=
EMAIL_SMTP_SERVER=
EMAIL_FROM=
EMAIL_TO=
ENVFILE
    echo -e "✓ .env file created (please update with your values)"
else
    echo -e "✓ .env file already exists"
fi

# Create systemd service file
echo -e "Creating systemd service..."
sudo tee /etc/systemd/system/network-agent.service > /dev/null << 'SERVICE'
[Unit]
Description=Network Operations Agent
After=network.target

[Service]
Type=simple
User=johnmarston
WorkingDirectory=/home/johnmarston/vandine-network-monitor/agent
Environment="PATH=/home/johnmarston/vandine-network-monitor/agent/venv/bin"
ExecStart=/home/johnmarston/vandine-network-monitor/agent/venv/bin/python /home/johnmarston/vandine-network-monitor/agent/pi-executor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

echo -e "✓ Systemd service created"

# Create agent launcher script
cat > run_agent.sh << 'LAUNCHER'
#!/bin/bash
cd /home/johnmarston/vandine-network-monitor/agent
source venv/bin/activate
python pi-executor.py
LAUNCHER
chmod +x run_agent.sh

echo ""
echo "==============================================="
echo -e "Setup Complete!"
echo "==============================================="
echo ""
echo "Next steps:"
echo "1. Update the .env file with your Cloudflare credentials"
echo "2. Start the agent:"
echo "   - Development: ./run_agent.sh"
echo "   - Production: sudo systemctl start network-agent"
echo "   - Enable on boot: sudo systemctl enable network-agent"
echo ""
echo "3. Deploy Cloudflare Worker:"
echo "   - Install wrangler: npm install -g wrangler"
echo "   - Deploy: wrangler deploy cloudflare-worker.js"
echo ""
echo "4. Access the agent:"
echo "   - API: http://192.168.2.7:8000"
echo "   - Docs: http://192.168.2.7:8000/docs"
echo ""
