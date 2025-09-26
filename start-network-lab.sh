#!/bin/bash
# Start Network Engineering Lab

# Install dependencies
pip3 install fastapi uvicorn httpx aioredis uvloop

# Start API Gateway
nohup python3 api/gateway_v2.py > logs/gateway_v2.log 2>&1 &
echo "Network Lab API started on port 8887"

# Update nginx
sudo sed -i 's/8888/8887/g' /etc/nginx/sites-available/vandine.us
sudo systemctl reload nginx

echo "Access Network Lab at: http://vandine.us/frontend/network-lab.html"
