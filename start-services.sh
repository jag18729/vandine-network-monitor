#!/bin/bash

# Vandine Network Monitor - Service Startup Script

echo "Starting Vandine Network Monitor Services..."

# Source environment variables
source .env

# Kill any existing services
pkill -f "node api/gateway/index.js" || true
pkill -f "python.*pihole_service.py" || true
pkill -f "python.*mongodb_service.py" || true

# Install dependencies if needed
echo "Checking dependencies..."
cd api/gateway
if [ ! -d "node_modules" ]; then
    echo "Installing API Gateway dependencies..."
    npm install
fi
cd ../..

cd api/services/pihole
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi
cd ../../..

# Start services
echo "Starting API Gateway on port 8888..."
nohup node api/gateway/index.js > logs/gateway.log 2>&1 &
echo "API Gateway PID: $!"

echo "Starting Pi-hole Service on port 8889..."
cd api/services/pihole
source .venv/bin/activate
nohup python pihole_service.py > ../../../logs/pihole.log 2>&1 &
echo "Pi-hole Service PID: $!"
cd ../../..

# MongoDB service is optional
# echo "Starting MongoDB Service on port 8890..."
# cd api/services/database
# nohup python mongodb_service.py > ../../../logs/mongodb.log 2>&1 &
# echo "MongoDB Service PID: $!"
# cd ../../..

sleep 3

echo ""
echo "Services started successfully!"
echo ""
echo "Access points:"
echo "  Main Dashboard: http://vandine.us"
echo "  DNS Analytics: http://vandine.us/frontend/dns-analytics.html"
echo "  Pi-hole Dashboard: http://vandine.us/frontend/pihole-dashboard.html"
echo "  API Gateway: http://192.168.2.7:8888/health"
echo "  Pi-hole Admin: http://192.168.2.7/admin"
echo ""
echo "Check logs in ./logs/ directory for service output"
