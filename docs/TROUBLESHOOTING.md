# Troubleshooting Guide

## Quick Diagnostics

### Check All Services
```bash
ssh pi1 "
echo '=== Core Services ==='
systemctl is-active nginx prometheus grafana-server alertmanager cloudflared

echo '=== Exporters ==='
systemctl is-active snmp_exporter node_exporter blackbox_exporter 2>/dev/null || docker ps | grep exporter

echo '=== API Services ==='
curl -s -o /dev/null -w 'API Gateway: %{http_code}\n' http://localhost:8887/health
curl -s -o /dev/null -w 'Pi-hole API: %{http_code}\n' http://localhost:8889/api/pihole/summary
"
```

## Common Issues

### 1. Site Not Loading (502/503/504)

**Symptoms**: Browser shows error page or timeout

**Diagnosis**:
```bash
# Check nginx
ssh pi1 "sudo nginx -t && systemctl status nginx"

# Check error logs
ssh pi1 "tail -20 /var/log/nginx/error.log"

# Check if backend services are running
ssh pi1 "curl -s http://localhost:8887/health"
```

**Solutions**:
- Restart nginx: `sudo systemctl restart nginx`
- Check backend service is running
- Verify proxy_pass URL in nginx config

### 2. Cloudflare 403 Forbidden

**Symptoms**: `cf-mitigated: challenge` in response headers

**Diagnosis**:
```bash
curl -sI https://vandine.us/ | grep -i "cf-mitigated\|http/"
```

**Solutions**:
1. Go to Cloudflare Dashboard → Security → Bots
2. Disable **Bot Fight Mode**
3. Or set Security Level to "Essentially Off"

### 3. SNMP Metrics Not Showing

**Symptoms**: Empty SNMP tab, no interface data

**Diagnosis**:
```bash
# Check SNMP exporter
ssh pi1 "curl -s 'http://localhost:9116/snmp?target=192.168.2.1&module=if_mib' | head -20"

# Check Prometheus scraping
ssh pi1 "curl -s 'http://localhost:9090/api/v1/query?query=up{job=\"snmp-udm\"}'"

# Check SNMP exporter logs
ssh pi1 "journalctl -u snmp_exporter --since '10 min ago'"
```

**Solutions**:
- Verify SNMPv3 credentials in snmp.yml
- Check UDM Pro SNMP is enabled
- Restart SNMP exporter: `sudo systemctl restart snmp_exporter`

### 4. Grafana Not Loading

**Symptoms**: /grafana/ shows blank page or redirect loop

**Diagnosis**:
```bash
ssh pi1 "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/"
ssh pi1 "systemctl status grafana-server"
```

**Solutions**:
- Check Grafana is running: `sudo systemctl restart grafana-server`
- Verify nginx proxy_pass points to correct port
- Check Grafana logs: `journalctl -u grafana-server -f`

### 5. Pi-hole Stats Not Updating

**Symptoms**: Dashboard shows "--" for blocked count

**Diagnosis**:
```bash
# Check Pi-hole API
ssh pi1 "curl -s http://localhost:8889/api/pihole/summary | head -c 200"

# Check Pi-hole FTL
ssh pi1 "systemctl status pihole-FTL"
```

**Solutions**:
- Restart Pi-hole: `pihole restartdns`
- Check API gateway: `sudo systemctl restart vandine-pihole`
- Verify API URL in dashboard JavaScript

### 6. Cloudflare Edge Shows "Unknown"

**Symptoms**: Edge location displays "Unknown (Unknown)"

**Diagnosis**:
```bash
# Test trace endpoint locally
ssh pi1 "curl -s http://localhost/cdn-cgi/trace | grep colo"

# Test through Cloudflare
curl -s https://vandine.us/cdn-cgi/trace | grep colo
```

**Solutions**:
- Cloudflare trace endpoint should return `colo=XXX`
- Check JavaScript uses `/cdn-cgi/trace` not external URL
- Clear browser cache and reload

### 7. WebSocket Connection Failed

**Symptoms**: Real-time updates not working, console shows WS errors

**Diagnosis**:
```bash
# Check WebSocket endpoint
ssh pi1 "curl -s -o /dev/null -w '%{http_code}' http://localhost:8887/ws/"
```

**Solutions**:
- Verify nginx has WebSocket headers:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  ```
- Check API gateway supports WebSocket

### 8. Docker Containers Not Starting

**Symptoms**: `docker ps` shows containers restarting

**Diagnosis**:
```bash
ssh pi1 "docker ps -a"
ssh pi1 "docker logs <container_name>"
```

**Solutions**:
- Check disk space: `df -h`
- Check memory: `free -h`
- Review container logs for specific errors
- Restart Docker: `sudo systemctl restart docker`

## Service-Specific Commands

### Nginx
```bash
# Test config
sudo nginx -t

# Reload without downtime
sudo systemctl reload nginx

# Full restart
sudo systemctl restart nginx

# View active connections
sudo nginx -V 2>&1 | grep -o 'with-http_stub_status'
```

### Prometheus
```bash
# Reload config (no restart)
curl -X POST http://localhost:9090/-/reload

# Check targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .job, health: .health}'

# Check config
curl -s http://localhost:9090/api/v1/status/config
```

### Grafana
```bash
# Reset admin password
grafana-cli admin reset-admin-password newpassword

# Check datasources
curl -s http://admin:admin@localhost:3000/api/datasources

# Restart
sudo systemctl restart grafana-server
```

### Cloudflared
```bash
# Check tunnel status
cloudflared tunnel info vandine

# View connections
cloudflared tunnel run vandine --protocol http2

# Restart tunnel
sudo systemctl restart cloudflared
```

## Log Locations

| Service | Log Location |
|---------|--------------|
| Nginx Access | /var/log/nginx/access.log |
| Nginx Error | /var/log/nginx/error.log |
| Prometheus | journalctl -u prometheus |
| Grafana | journalctl -u grafana-server |
| Cloudflared | journalctl -u cloudflared |
| SNMP Exporter | journalctl -u snmp_exporter |
| Docker | docker logs <container> |
| System | /var/log/syslog |

## Performance Issues

### High CPU Usage
```bash
# Find culprit
top -c

# Check Prometheus memory
curl -s http://localhost:9090/api/v1/status/runtimeinfo | jq '.data'
```

### High Memory Usage
```bash
# Check memory
free -h

# Docker memory
docker stats --no-stream

# Prometheus TSDB
curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data'
```

### Disk Space Issues
```bash
# Check disk
df -h

# Find large files
du -sh /var/lib/* | sort -h | tail -10

# Clean Docker
docker system prune -a
```

## Network Debugging

### Test Internal Connectivity
```bash
# From Pi to services
curl -s http://localhost:9090/-/healthy  # Prometheus
curl -s http://localhost:3000/api/health  # Grafana
curl -s http://localhost:9116/metrics     # SNMP Exporter
```

### Test External Connectivity
```bash
# DNS resolution
dig vandine.us +short

# HTTP through Cloudflare
curl -sI https://vandine.us/ | head -10

# Latency
ping -c 5 vandine.us
```

### Test SNMP
```bash
# SNMPv3 walk
snmpwalk -v3 -l authPriv -u snmpuser -a SHA -A "authpass" -x AES -X "privpass" 192.168.2.1 1.3.6.1.2.1.1.1.0
```

## Emergency Recovery

### Complete Service Restart
```bash
ssh pi1 "
sudo systemctl restart nginx
sudo systemctl restart prometheus
sudo systemctl restart grafana-server
sudo systemctl restart alertmanager
sudo systemctl restart cloudflared
docker restart \$(docker ps -q)
"
```

### Restore from Backup
```bash
# List backups
ssh pi1 "ls -la /var/www/vandine.us/*.backup*"

# Restore
ssh pi1 "sudo cp /var/www/vandine.us/index.html.backup-LATEST /var/www/vandine.us/index.html"
```

### Factory Reset Dashboard
```bash
# Pull fresh from git
cd /home/johnmarston/vandine-network-monitor
git fetch origin
git reset --hard origin/main
sudo cp index.html /var/www/vandine.us/
```
