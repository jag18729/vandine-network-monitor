# Nginx Configuration Guide

## Overview

Nginx serves as the reverse proxy for all services, handling SSL termination (via Cloudflare), routing, and static file serving.

## Configuration Files

### Main Sites
```
/etc/nginx/sites-enabled/
├── vandine.us       # Main NOC dashboard
├── revealtome.us    # Portfolio site
└── pihole           # Pi-hole admin (legacy)
```

## vandine.us Configuration

```nginx
# Main vandine.us site
server {
    listen 80;
    listen 443 ssl http2;
    server_name vandine.us www.vandine.us;

    # SSL (self-signed, Cloudflare handles public SSL)
    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/vandine.us;
    index index.html;

    # API Gateway
    location /api/ {
        proxy_pass http://127.0.0.1:8887/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location = /health {
        proxy_pass http://127.0.0.1:8887/health;
        proxy_set_header Host $host;
    }

    # Prometheus
    location /prometheus/ {
        proxy_pass http://127.0.0.1:9090/;
        proxy_set_header Host $host;
    }

    # Grafana
    location /grafana/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Pi-hole Admin
    location /pihole/ {
        proxy_pass http://127.0.0.1:8080/admin/;
        proxy_set_header Host $host;
    }

    # Alertmanager
    location /alertmanager/ {
        proxy_pass http://127.0.0.1:9093/;
        proxy_set_header Host $host;
    }

    # Blackbox Exporter
    location /blackbox/ {
        proxy_pass http://127.0.0.1:9115/;
        proxy_set_header Host $host;
    }

    # SNMP Exporter
    location /snmp/ {
        proxy_pass http://127.0.0.1:9116/;
        proxy_set_header Host $host;
    }

    # Node Exporter
    location /node-metrics/ {
        proxy_pass http://127.0.0.1:9100/;
        proxy_set_header Host $host;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8887/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Portfolio site at /reveal
    location /reveal/assets/ {
        alias /var/www/html/assets/;
    }

    location /reveal {
        alias /var/www/html;
        index index.html;
        try_files $uri $uri/ /reveal/index.html;
    }

    # Root assets for React app
    location /assets/ {
        alias /var/www/html/assets/;
    }

    # Static files
    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Adding a New Proxy Location

### Basic Proxy
```nginx
location /newservice/ {
    proxy_pass http://127.0.0.1:PORT/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### With WebSocket Support
```nginx
location /newservice/ {
    proxy_pass http://127.0.0.1:PORT/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400;
}
```

### With Authentication
```nginx
location /newservice/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:PORT/;
}
```

## Common Operations

### Test Configuration
```bash
sudo nginx -t
```

### Reload Configuration
```bash
sudo systemctl reload nginx
```

### View Access Logs
```bash
tail -f /var/log/nginx/access.log
```

### View Error Logs
```bash
tail -f /var/log/nginx/error.log
```

### Check Status
```bash
systemctl status nginx
```

## Troubleshooting

### 502 Bad Gateway
- Backend service not running
- Wrong port number
- Firewall blocking connection

```bash
# Check if backend is running
curl -s http://localhost:PORT/
```

### 404 Not Found
- Wrong location path
- Missing try_files directive
- Root/alias path incorrect

### 403 Forbidden
- Directory listing disabled
- Permission denied on files
- Missing index file

```bash
# Check permissions
ls -la /var/www/vandine.us/
```

### WebSocket Connection Failed
- Missing upgrade headers
- Proxy timeout too short
- Missing http_version 1.1

## SSL Certificate Setup

### Generate Self-Signed Certificate
```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/CN=vandine.us"
```

### Using Let's Encrypt (if not using Cloudflare)
```bash
sudo certbot --nginx -d vandine.us -d www.vandine.us
```

## Performance Tuning

### Enable Gzip
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

### Enable Caching
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### Connection Limits
```nginx
worker_connections 1024;
keepalive_timeout 65;
```

## File Locations Reference

| Path | Purpose |
|------|---------|
| /etc/nginx/nginx.conf | Main config |
| /etc/nginx/sites-available/ | Site configs (available) |
| /etc/nginx/sites-enabled/ | Site configs (enabled) |
| /var/www/vandine.us/ | NOC dashboard files |
| /var/www/html/ | Portfolio/default site |
| /var/log/nginx/ | Log files |
| /etc/nginx/ssl/ | SSL certificates |
