# Vandine Network Monitor & Intelligent Agent System

## 🎯 Project Intent

This project showcases advanced network engineering and DevOps practices through a comprehensive monitoring and automation platform. It demonstrates:

- **Enterprise Network Architecture**: Palo Alto PA-220 firewall, VLANs, IPsec tunnels
- **Edge Computing**: Cloudflare Workers and CDN integration  
- **Automation**: Intelligent agent system for network task management
- **CI/CD**: GitHub Actions with dev/staging/production pipelines
- **Infrastructure as Code**: Automated deployment and configuration

## 🏗️ Architecture

### Network Infrastructure
- **Firewall**: Palo Alto PA-220 Next-Gen Firewall
- **VLANs**: Segmented networks (10.200.1.0/24, 10.201.1.0/24)
- **VPN**: IPsec tunnels with AES-256-GCM encryption
- **CDN**: Cloudflare edge network (LAX point of presence)
- **DNS**: Dynamic DNS via rafael.vandine.us

### Agent System Architecture

    API Gateway (Port 8888) - Intelligent Task Routing
           |                    |                |
    Cloudflare API       Worker (8787)    Pi Exec (8000)
    DNS, Cache          Task Queue       System Metrics
    SSL, Rules          Analytics        Health Checks

## 🚀 Features

### Current Capabilities
- Real-time network monitoring dashboard
- Cloudflare edge location detection
- Performance metrics visualization
- Intelligent task routing via API Gateway
- Multi-service orchestration
- Automated CI/CD pipeline
- Git worktree for branch management

### Agent Task Types
- **DNS Management**: Update/create DNS records
- **Cache Operations**: Purge CDN cache
- **SSL Monitoring**: Certificate verification
- **Firewall Rules**: Security configuration
- **System Metrics**: CPU, memory, disk monitoring
- **Health Checks**: Service availability
- **Security Scans**: Hybrid security analysis

## 📦 Installation

### Prerequisites
- Raspberry Pi 4 (8GB RAM recommended)
- Node.js 22.x LTS
- Python 3.11+
- nginx
- systemd

### Quick Setup

    # Clone repository
    git clone https://github.com/jag18729/vandine-network-monitor.git
    cd vandine-network-monitor

    # Run setup script
    cd agent
    ./setup_agent.sh

    # Configure credentials
    ./get_cloudflare_info.py

## 🔧 Services

### System Services
| Service | Port | Description | Status Check |
|---------|------|-------------|--------------|
| vandine-agent | 8000 | Pi Executor - System tasks | systemctl status vandine-agent |
| vandine-worker | 8787 | Worker Simulator - Task queue | systemctl status vandine-worker |
| vandine-gateway | 8888 | API Gateway - Task routing | systemctl status vandine-gateway |

### Web Interfaces
- **Main Dashboard**: http://192.168.2.7/vandine-showcase.html
- **Agent Control**: http://192.168.2.7/agent-dashboard.html
- **API Status**: http://192.168.2.7:8888/api/v1/status

## 📡 API Documentation

### Create Task

    curl -X POST http://192.168.2.7:8888/api/v1/tasks \
      -H "Content-Type: application/json" \
      -d '{
        "type": "dns_update",
        "priority": "high",
        "data": {
          "record": "api.vandine.us",
          "type": "A",
          "content": "192.168.1.100"
        }
      }'

### Get Status

    curl http://192.168.2.7:8888/api/v1/status

### View Capabilities

    curl http://192.168.2.7:8888/api/v1/capabilities

## 🔄 CI/CD Pipeline

### Branch Strategy
- **main**: Production (protected)
- **staging**: Pre-production testing
- **dev**: Active development

### GitHub Actions
- **Deploy**: Automated deployment on push
- **Monitor**: Hourly health checks
- **Security**: Secret scanning and validation

## 🛠️ Development

### Local Development

    # Activate Python environment
    cd agent
    source venv/bin/activate

    # Run tests
    python test_agent.py

    # Check logs
    journalctl -u vandine-agent -f
    journalctl -u vandine-worker -f
    journalctl -u vandine-gateway -f

### Git Worktree Setup

    cd /home/johnmarston/vandine-network-monitor-staging  # staging branch
    cd /home/johnmarston/vandine-network-monitor-prod     # main branch

## 📊 Monitoring

### Metrics Collection
- System: CPU, Memory, Disk usage
- Network: Latency, throughput, packet loss
- Services: nginx, Docker, agent health
- Cloudflare: Edge location, cache hit rate

## 🗺️ Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Network showcase website
- [x] Agent system deployment
- [x] API Gateway implementation
- [x] CI/CD pipeline

### Phase 2: Enhanced Automation (Current)
- [ ] Cloudflare SDK full integration
- [ ] Automated DNS management
- [ ] Traffic analytics dashboard
- [ ] Rate limiting controls

### Phase 3: Advanced Features
- [ ] ML-based anomaly detection
- [ ] Predictive scaling
- [ ] Multi-region failover
- [ ] Kubernetes integration

### Phase 4: Enterprise Features
- [ ] SAML/SSO authentication
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Compliance reporting

## 🔐 Security

- API authentication via Bearer tokens
- HTTPS enforcement via Cloudflare
- Firewall rules via PA-220
- Regular security scans
- No credentials in repository

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📧 Contact

- GitHub: @jag18729
- Project: vandine-network-monitor

---
Built with passion for network engineers and DevOps professionals
