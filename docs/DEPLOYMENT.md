# Deployment Guide

## Overview

This guide covers deploying and updating the Vandine NOC dashboard and associated services.

## Quick Deployment

### Deploy Dashboard Changes
```bash
# From local machine
scp index.html pi1:/var/www/vandine.us/index.html
ssh pi1 "sudo chown www-data:www-data /var/www/vandine.us/index.html"
```

### Using Claude Code Skill
```
/deploy-vandine
```

## Full Stack Deployment

### Prerequisites
- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspbian OS / Debian
- Docker & Docker Compose
- SSH access configured

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx docker.io docker-compose git curl

# Enable Docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. Clone Repository

```bash
cd /home/johnmarston
git clone https://github.com/jag18729/vandine-network-monitor.git
cd vandine-network-monitor
```

### 3. Deploy Services

```bash
# Start monitoring stack
docker-compose -f docker-compose.pi.yml up -d

# Or use the deploy script
./deploy.sh
```

### 4. Configure Nginx

```bash
# Copy site configuration
sudo cp nginx/vandine.us /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/vandine.us /etc/nginx/sites-enabled/

# Copy dashboard files
sudo mkdir -p /var/www/vandine.us
sudo cp index.html /var/www/vandine.us/
sudo chown -R www-data:www-data /var/www/vandine.us

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Setup Cloudflare Tunnel

```bash
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb

# Authenticate and create tunnel
cloudflared tunnel login
cloudflared tunnel create vandine

# Install as service
sudo cloudflared service install
sudo systemctl enable cloudflared
```

## Updating Components

### Update Dashboard Only
```bash
# Pull latest from git
git pull origin main

# Deploy to server
scp index.html pi1:/var/www/vandine.us/
```

### Update Docker Services
```bash
# SSH to Pi
ssh pi1

# Pull latest images
cd /home/johnmarston/vandine-network-monitor
docker-compose pull

# Restart services
docker-compose down && docker-compose up -d
```

### Update Nginx Configuration
```bash
# Edit configuration
ssh pi1 "sudo nano /etc/nginx/sites-enabled/vandine.us"

# Test and reload
ssh pi1 "sudo nginx -t && sudo systemctl reload nginx"
```

### Update Prometheus Configuration
```bash
# Edit prometheus.yml
ssh pi1 "sudo nano /etc/prometheus/prometheus.yml"

# Reload (without restart)
ssh pi1 "curl -X POST http://localhost:9090/-/reload"

# Or restart service
ssh pi1 "sudo systemctl restart prometheus"
```

## Rollback Procedures

### Dashboard Rollback
```bash
# List backups
ssh pi1 "ls -la /var/www/vandine.us/*.backup*"

# Restore specific backup
ssh pi1 "sudo cp /var/www/vandine.us/index.html.backup-YYYYMMDD /var/www/vandine.us/index.html"
```

### Docker Rollback
```bash
# Stop current containers
docker-compose down

# Checkout previous version
git checkout HEAD~1

# Restart
docker-compose up -d
```

## Health Checks

### Post-Deployment Verification
```bash
# Check nginx
ssh pi1 "sudo nginx -t && systemctl is-active nginx"

# Check site accessibility
curl -s -o /dev/null -w "%{http_code}" http://pi1/

# Check all services
ssh pi1 "docker ps"

# Check Cloudflare tunnel
ssh pi1 "systemctl is-active cloudflared"
```

### Service Status Commands
```bash
# All services at once
ssh pi1 "systemctl is-active nginx prometheus grafana-server cloudflared"

# Docker containers
ssh pi1 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# API health
ssh pi1 "curl -s http://localhost:8887/health"
```

## CI/CD with GitHub Actions

### Workflow File
`.github/workflows/deploy.yml`:
```yaml
name: Deploy to Pi

on:
  push:
    branches: [main]
    paths:
      - 'index.html'
      - 'docker-compose*.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PI_HOST }}
          username: ${{ secrets.PI_USER }}
          key: ${{ secrets.PI_SSH_KEY }}
          script: |
            cd /home/johnmarston/vandine-network-monitor
            git pull origin main
            sudo cp index.html /var/www/vandine.us/
            sudo systemctl reload nginx
```

## Environment Variables

### Required Secrets
| Secret | Description |
|--------|-------------|
| `PI_HOST` | Pi server hostname/IP |
| `PI_USER` | SSH username |
| `PI_SSH_KEY` | SSH private key |
| `CF_API_TOKEN` | Cloudflare API token |

## Monitoring Deployment

### Check Deployment Status
1. Visit https://vandine.us/
2. Check version in footer or console
3. Verify all services in quick links work

### Smoke Tests
```bash
# Test main page
curl -s https://vandine.us/ | grep -o '<title>.*</title>'

# Test API
curl -s https://vandine.us/api/status

# Test Grafana
curl -s -o /dev/null -w "%{http_code}" https://vandine.us/grafana/

# Test Prometheus
curl -s https://vandine.us/prometheus/api/v1/status/config | head -c 100
```

## File Locations Summary

| Component | Location |
|-----------|----------|
| Dashboard HTML | /var/www/vandine.us/index.html |
| Portfolio Site | /var/www/html/ |
| Nginx Config | /etc/nginx/sites-enabled/vandine.us |
| Prometheus Config | /etc/prometheus/prometheus.yml |
| SNMP Config | /etc/snmp_exporter/snmp.yml |
| Grafana Data | /var/lib/grafana/ |
| Cloudflared Config | ~/.cloudflared/config.yml |
| Docker Compose | /home/johnmarston/vandine-network-monitor/ |
