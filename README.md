# Vandine Zero-Trust Network Operations Center

A production-grade network engineering showcase featuring multi-site infrastructure with advanced routing, monitoring, and security capabilities.

## Live Demo
Visit: [vandine.us](https://vandine.us)

## Recent Updates (January 2026)

### Enhanced Dashboard UI
- **Glassmorphism Design** - Modern frosted glass effects with backdrop blur
- **Animated Background** - Subtle gradient shifts with floating particle effects
- **Grid Overlay** - Tech-inspired grid pattern for NOC aesthetic
- **Glowing Status Indicators** - Animated pulse effects for online/offline states
- **Smooth Transitions** - CSS cubic-bezier animations throughout

### SNMP Monitoring
- **Real-time Interface Metrics** - Live data from UDM Pro via SNMPv3 (SHA+AES)
- **Traffic Visualization** - Bandwidth graphs for all 59+ interfaces
- **Filterable Interface Table** - Sort and filter by status, traffic, errors
- **Query Console** - Direct PromQL queries against SNMP metrics

### Cloudflare Integration
- **Edge Location Detection** - Auto-detect nearest Cloudflare PoP
- **Latency Measurement** - Real-time round-trip timing
- **Argo Smart Routing** - Optimized traffic paths enabled

## Features

### Infrastructure Components
- **Palo Alto PA-220** - Next-generation firewall with IPS/IDS, URL filtering, and threat prevention
- **UniFi Dream Machine Pro** - Core router with 59 interfaces monitored via SNMP
- **Cloudflare Edge Network** - Global CDN with 275+ PoPs, Argo Tunnel connectivity
- **Raspberry Pi Cluster** - Distributed services (Pi-hole DNS, Prometheus, Grafana)
- **Dynamic DNS** - Automatic failover with 60-second TTL updates
- **IPsec VPN** - Site-to-site connectivity with AES-256-GCM encryption
- **VLAN Segmentation** - Isolated networks for security

### Monitoring Stack
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization dashboards
- **SNMP Exporter** - Network device metrics (UDM Pro, switches)
- **Blackbox Exporter** - Endpoint probing and latency
- **Node Exporter** - System metrics from all hosts
- **Alertmanager** - Alert routing and notifications
- **Pi-hole** - DNS filtering with API integration

### Dashboard Pages
| Page | Description |
|------|-------------|
| Infrastructure | Device status overview with live metrics |
| Palo Alto PA-220 | Firewall stats, sessions, threats |
| Cloudflare Edge | CDN metrics, edge location, latency |
| Route Testing | Compare Cloudflare vs direct routes |
| UniFi Dream Machine | Client counts, traffic stats |
| Raspberry Pi Cluster | Service health, resource usage |
| Zero Trust | Security posture, trust levels |
| Automation | Self-healing status, event logs |
| SNMP Monitor | Real-time interface metrics |

### Key Capabilities
- Multi-site connectivity with automatic failover
- Hardware-accelerated inter-VLAN routing
- Zero-trust security architecture
- Self-healing infrastructure with automated remediation
- 99.9% uptime SLA
- Sub-20ms latency via Cloudflare edge
- 950+ Mbps throughput capacity

## Network Topology

```
Internet --> vandine.us (Cloudflare Tunnel) --> Cloudflare Edge (LAX)
                                                      |
                                               Argo Tunnel
                                                      |
                                              Pi-1 (192.168.2.70)
                                                      |
                                              UDM Pro Router
                                                      |
                                    +-----------------+-----------------+
                                    |                 |                 |
                              VLAN 200           VLAN 201          Management
                           10.200.1.0/24      10.201.1.0/24       192.168.2.0/24
```

## Technology Stack

| Category | Technology |
|----------|------------|
| Security | Palo Alto PA-220 NGFW, Cloudflare WAF |
| CDN/Edge | Cloudflare Workers, Argo Tunnel |
| VPN | IPsec IKEv2 with PFS |
| Web Server | nginx with reverse proxy |
| Monitoring | Prometheus, Grafana, SNMP Exporter |
| DNS | Pi-hole with API gateway |
| Containers | Docker & Docker Compose |
| Frontend | Vanilla JS with CSS animations |

## Performance Metrics

| Route Type | Latency | Throughput | Packet Loss |
|------------|---------|------------|-------------|
| Cloudflare Argo | 18ms | 948 Mbps | 0.01% |
| Direct ISP | 35ms | 756 Mbps | 0.1% |
| IPsec Tunnel | 22ms | 856 Mbps | 0% |

## API Endpoints

| Endpoint | Port | Description |
|----------|------|-------------|
| `/api/status` | 8887 | Service health check |
| `/api/pihole/summary` | 8889 | Pi-hole statistics |
| `/grafana/` | 3000 | Grafana dashboards |
| `/prometheus/` | 9090 | Prometheus UI |
| `/alertmanager/` | 9093 | Alert management |
| `/snmp/` | 9116 | SNMP exporter metrics |

## Future Enhancements

### Planned Features
- [ ] **NetFlow/sFlow Integration** - Traffic flow analysis and visualization
- [ ] **Automated Topology Discovery** - LLDP/CDP neighbor mapping
- [ ] **Historical Trending** - Long-term metric storage and analysis
- [ ] **Anomaly Detection** - ML-based traffic pattern analysis
- [ ] **Multi-tenant Support** - Role-based access control
- [ ] **Mobile Responsive** - Optimized tablet/phone layouts
- [ ] **Dark/Light Theme Toggle** - User preference persistence
- [ ] **Webhook Integrations** - Slack, Discord, PagerDuty alerts
- [ ] **Config Backup** - Automated device configuration snapshots
- [ ] **Bandwidth Reports** - Scheduled PDF/email reports

### Infrastructure Improvements
- [ ] **High Availability** - Active/passive failover for critical services
- [ ] **Geographic Redundancy** - Multi-region deployment
- [ ] **IPv6 Support** - Dual-stack networking throughout
- [ ] **802.1X Authentication** - Port-based network access control
- [ ] **RADIUS Integration** - Centralized authentication

### Monitoring Enhancements
- [ ] **Custom Grafana Dashboards** - Pre-built NOC views
- [ ] **SLA Monitoring** - Uptime tracking with SLO/SLI metrics
- [ ] **Capacity Planning** - Resource utilization forecasting
- [ ] **Log Aggregation** - Centralized logging with Loki
- [ ] **Distributed Tracing** - Request flow visualization

## Local Development

```bash
# Clone the repository
git clone https://github.com/jag18729/vandine-network-monitor.git
cd vandine-network-monitor

# Deploy to Pi cluster
./deploy.sh

# Or use Docker Compose
docker-compose up -d
```

## Security Features

- Zero-trust network architecture
- Multi-layer security (DDoS, WAF, NGFW)
- IPsec encryption for site-to-site VPN
- VLAN isolation for network segmentation
- Real-time threat detection and response
- SNMPv3 with SHA authentication and AES encryption

## Documentation

Comprehensive documentation available in [`/docs`](docs/):

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System topology, service dependencies, security layers |
| [SNMP_MONITORING.md](docs/SNMP_MONITORING.md) | SNMPv3 setup, metrics reference, PromQL queries |
| [NGINX_CONFIGURATION.md](docs/NGINX_CONFIGURATION.md) | Reverse proxy, SSL, adding new services |
| [CLOUDFLARE_SETUP.md](docs/CLOUDFLARE_SETUP.md) | Argo Tunnel, DNS, security settings |
| [DASHBOARD_FEATURES.md](docs/DASHBOARD_FEATURES.md) | UI components, animations, responsive design |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment guide, CI/CD, rollback procedures |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues, diagnostics, recovery |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | All endpoints, PromQL examples |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and accomplishments |

## License

MIT License

---

Built for network engineers by network engineers | [GitHub](https://github.com/jag18729) | [Reveal.me](https://vandine.us/reveal/)
