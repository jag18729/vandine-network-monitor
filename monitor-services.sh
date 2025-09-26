#!/bin/bash

# Vandine Network Monitor - Service Health Monitor
# This script checks service health and restarts if needed

LOG_DIR="/home/johnmarston/vandine-network-monitor/logs"
HEALTH_LOG="${LOG_DIR}/health-monitor.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$HEALTH_LOG"
}

# Function to check service health
check_service() {
    local service_name=$1
    local health_endpoint=$2
    local port=$3
    
    # Check if service is responding
    if curl -s -f -m 5 "$health_endpoint" > /dev/null 2>&1; then
        log_message "✓ ${service_name} is healthy"
        return 0
    else
        log_message "✗ ${service_name} is not responding on port ${port}"
        return 1
    fi
}

# Function to restart service
restart_service() {
    local service_name=$1
    log_message "Restarting ${service_name}..."
    sudo systemctl restart "vandine-${service_name}.service"
    sleep 5
}

# Main monitoring loop
log_message "Starting health monitor..."

# Check API Gateway
if ! check_service "API Gateway" "http://localhost:8887/health" "8887"; then
    restart_service "gateway"
fi

# Check Pi-hole Service
if ! check_service "Pi-hole Service" "http://localhost:8889/health" "8889"; then
    restart_service "pihole"
fi

# Check MongoDB Service (if enabled)
# if ! check_service "MongoDB Service" "http://localhost:8890/health" "8890"; then
#     restart_service "mongodb"
# fi

# Check nginx
if ! systemctl is-active --quiet nginx; then
    log_message "✗ Nginx is not running, starting..."
    sudo systemctl start nginx
fi

# Check Pi-hole DNS
if ! systemctl is-active --quiet pihole-FTL; then
    log_message "✗ Pi-hole FTL is not running, starting..."
    sudo systemctl start pihole-FTL
fi

# Report overall status
log_message "Health check completed"
