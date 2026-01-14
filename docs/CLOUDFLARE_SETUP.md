# Cloudflare Configuration Guide

## Overview

The Vandine NOC uses Cloudflare Tunnel (Argo Tunnel) for secure external access without exposing ports to the internet.

## Architecture

```
Internet → Cloudflare Edge (LAX) → Argo Tunnel → Pi-1 (nginx) → Services
```

## Cloudflare Tunnel Setup

### Install cloudflared
```bash
# Download and install
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create vandine
```

### Configuration File
Location: `~/.cloudflared/config.yml`

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/johnmarston/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: vandine.us
    service: http://localhost:80
  - hostname: www.vandine.us
    service: http://localhost:80
  - hostname: reveal.vandine.us
    service: http://localhost:80
  - service: http_status:404
```

### Run as Service
```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

## DNS Configuration

### Required Records

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | @ | `<TUNNEL_ID>.cfargotunnel.com` | Proxied (Orange) |
| CNAME | www | `<TUNNEL_ID>.cfargotunnel.com` | Proxied (Orange) |
| CNAME | reveal | vandine.us | Proxied (Orange) |

### Important Notes
- **Proxied (Orange Cloud)**: Required for Argo Tunnel to work
- **DNS Only (Gray Cloud)**: Won't work with Argo Tunnel

## Security Settings

### Recommended Configuration

#### SSL/TLS
- **Encryption Mode**: Full (strict)
- **Always Use HTTPS**: On
- **Minimum TLS Version**: 1.2

#### Security
- **Security Level**: Medium (or Essentially Off for API access)
- **Bot Fight Mode**: Off (causes issues with curl/API calls)
- **Challenge Passage**: 30 minutes

#### Firewall Rules
Create rules to allow legitimate traffic:
```
(http.host eq "vandine.us") → Skip security
```

### Bot Fight Mode Issues

If you see `cf-mitigated: challenge` in responses:

1. Go to **Security** → **Bots**
2. Disable **Bot Fight Mode**
3. Or set **Security Level** to "Essentially Off"

## Edge Detection

The dashboard auto-detects the Cloudflare edge location using:
```javascript
fetch('/cdn-cgi/trace')
```

Response format:
```
fl=...
h=vandine.us
ip=xxx.xxx.xxx.xxx
ts=1234567890
visit_scheme=https
uag=Mozilla/5.0...
colo=LAX
...
```

### Edge Location Codes

| Code | City |
|------|------|
| LAX | Los Angeles |
| SJC | San Jose |
| SFO | San Francisco |
| SEA | Seattle |
| DFW | Dallas |
| ORD | Chicago |
| ATL | Atlanta |
| IAD | Washington DC |
| JFK | New York |
| MIA | Miami |
| DEN | Denver |
| PHX | Phoenix |

## Troubleshooting

### Test DNS Resolution
```bash
dig vandine.us +short
# Should return Cloudflare IPs (104.x.x.x, 172.x.x.x)
```

### Test Tunnel Connectivity
```bash
curl -I https://vandine.us/
# Look for cf-ray header
```

### Check for Security Challenges
```bash
curl -sI https://vandine.us/ | grep -i "cf-mitigated"
# If present, Bot Fight Mode or WAF is blocking
```

### View Tunnel Status
```bash
cloudflared tunnel info vandine
```

### Check cloudflared Service
```bash
sudo systemctl status cloudflared
journalctl -u cloudflared -f
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 403 Forbidden | Bot Fight Mode | Disable in Security → Bots |
| 522 Connection Timed Out | Origin not responding | Check nginx/cloudflared |
| 524 Timeout | Origin too slow | Increase timeout or optimize |
| ERR_SSL | SSL mode mismatch | Set to Full or Full (strict) |

## Performance Features

### Argo Smart Routing
- Automatically routes traffic through fastest paths
- Reduces latency by 30% average
- Enable in **Traffic** → **Argo**

### Caching
Page Rules for caching:
```
*.vandine.us/assets/*
  Cache Level: Cache Everything
  Edge Cache TTL: 7 days
```

### Polish & Mirage
- **Polish**: Image optimization
- **Mirage**: Lazy loading for mobile

## API Access

### Cloudflare API
```bash
# Get zone info
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json"
```

### Useful API Endpoints
- `/zones` - List zones
- `/zones/:id/dns_records` - DNS records
- `/zones/:id/analytics` - Traffic analytics
- `/zones/:id/settings` - Zone settings

## Subdomains

### Adding a New Subdomain

1. **Add DNS Record**:
   - Type: CNAME
   - Name: `newsub`
   - Target: `vandine.us`
   - Proxy: Enabled (Orange)

2. **Update Tunnel Config**:
   ```yaml
   ingress:
     - hostname: newsub.vandine.us
       service: http://localhost:80
   ```

3. **Restart cloudflared**:
   ```bash
   sudo systemctl restart cloudflared
   ```

4. **Update nginx**:
   ```nginx
   server_name vandine.us www.vandine.us newsub.vandine.us;
   ```

5. **Reload nginx**:
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```
