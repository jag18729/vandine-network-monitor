# Vandine NOC Architecture

## Overview

The Vandine Network Operations Center is a self-hosted monitoring solution running on a Raspberry Pi cluster, accessible via Cloudflare Tunnel.

## Network Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE EDGE (LAX)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  WAF/DDoS   │  │ Argo Smart  │  │    SSL      │  │   Caching   │    │
│  │ Protection  │  │   Routing   │  │ Termination │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                            Argo Tunnel (cloudflared)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Pi-1 (192.168.2.70) - Primary                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         NGINX (Port 80/443)                      │   │
│  │  /           → /var/www/vandine.us (NOC Dashboard)               │   │
│  │  /reveal/    → /var/www/html (Portfolio Site)                    │   │
│  │  /grafana/   → localhost:3000                                    │   │
│  │  /prometheus/→ localhost:9090                                    │   │
│  │  /pihole/    → localhost:8080                                    │   │
│  │  /alertmanager/ → localhost:9093                                 │   │
│  │  /snmp/      → localhost:9116                                    │   │
│  │  /api/       → localhost:8887                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Grafana    │ │  Prometheus  │ │   Pi-hole    │ │ Alertmanager │   │
│  │   :3000      │ │    :9090     │ │    :8080     │ │    :9093     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │SNMP Exporter │ │Node Exporter │ │  Blackbox    │ │ API Gateway  │   │
│  │   :9116      │ │    :9100     │ │    :9115     │ │    :8887     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     UDM Pro (192.168.2.1) - Core Router                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SNMPv3 (SHA+AES) → 59 Interfaces Monitored                     │   │
│  │  - WAN interfaces (eth8, eth9)                                   │   │
│  │  - LAN ports (eth0-eth7)                                         │   │
│  │  - VLANs, bridges, tunnels                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Network Segments:                                                      │
│  ├── 192.168.2.0/24  - Management/Default                              │
│  ├── 10.200.1.0/24   - VLAN 200 (Primary)                              │
│  └── 10.201.1.0/24   - VLAN 201 (Secondary)                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Service Dependencies

```
cloudflared ──► nginx ──┬──► Grafana (:3000)
                        ├──► Prometheus (:9090) ──┬──► SNMP Exporter (:9116) ──► UDM Pro
                        │                         ├──► Node Exporter (:9100)
                        │                         ├──► Blackbox (:9115)
                        │                         └──► Alertmanager (:9093)
                        ├──► Pi-hole (:8080)
                        └──► API Gateway (:8887) ──► Pi-hole API (:8889)
```

## Key Components

### 1. Cloudflare Tunnel (cloudflared)
- Provides secure external access without opening firewall ports
- Handles SSL termination at the edge
- Enables Argo Smart Routing for optimized paths

### 2. Nginx Reverse Proxy
- Routes all traffic to appropriate backend services
- Serves static files for the NOC dashboard
- Handles WebSocket upgrades for real-time data

### 3. Prometheus Stack
- **Prometheus**: Time-series database for metrics
- **Grafana**: Visualization and dashboarding
- **Alertmanager**: Alert routing and notification

### 4. SNMP Monitoring
- SNMPv3 with SHA authentication and AES encryption
- Monitors UDM Pro interfaces, traffic, and status
- Collects IF-MIB metrics (ifHCInOctets, ifHCOutOctets, ifOperStatus)

### 5. DNS Filtering (Pi-hole)
- Network-wide ad blocking
- DNS query logging and analytics
- Custom API gateway for dashboard integration

## Data Flow

### Metrics Collection
```
UDM Pro ──(SNMPv3)──► SNMP Exporter ──(HTTP)──► Prometheus ──(PromQL)──► Grafana
                                                     │
                                                     ▼
                                              Alertmanager ──► Notifications
```

### User Request Flow
```
User ──(HTTPS)──► Cloudflare ──(Tunnel)──► nginx ──► Backend Service
                     │
                     └── WAF, DDoS Protection, Caching
```

## Security Layers

| Layer | Protection |
|-------|------------|
| Edge | Cloudflare WAF, DDoS mitigation, Bot Fight Mode |
| Transport | TLS 1.3, Argo Tunnel encryption |
| Network | VLAN segmentation, firewall rules |
| Application | SNMPv3 authPriv, API authentication |
| Host | UFW firewall, fail2ban, SSH key-only |

## Port Reference

| Port | Service | Access |
|------|---------|--------|
| 80/443 | nginx | Via Cloudflare |
| 3000 | Grafana | Internal/Proxied |
| 9090 | Prometheus | Internal/Proxied |
| 9093 | Alertmanager | Internal/Proxied |
| 9100 | Node Exporter | Internal |
| 9115 | Blackbox Exporter | Internal/Proxied |
| 9116 | SNMP Exporter | Internal/Proxied |
| 8080 | Pi-hole Admin | Internal/Proxied |
| 8887 | API Gateway | Internal/Proxied |
| 8889 | Pi-hole API | Internal |
