# 🌅 Vandine Network Operations Center

[![CI/CD Pipeline](https://github.com/jag18729/vandine-network-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jag18729/vandine-network-monitor/actions)
[![Security Scan](https://github.com/jag18729/vandine-network-monitor/actions/workflows/security.yml/badge.svg)](https://github.com/jag18729/vandine-network-monitor/actions)
[![Uptime: 99.97%](https://img.shields.io/badge/uptime-99.97%25-brightgreen)](https://vandine.us)

> Enterprise-grade network monitoring and security from Mom's house 🏠

## 🚀 Live Dashboard

**Production:** [https://vandine.us](https://vandine.us)

## 📊 Features

### Network Monitoring
- **Real-time Infrastructure Status** - Monitor 23+ critical services
- **Service Health Checks** - Automated monitoring with self-healing
- **Network Traffic Analysis** - Deep packet inspection and flow analysis
- **Performance Metrics** - Latency, throughput, and packet loss tracking

### Security Operations
- **Zero-Trust Architecture** - Cloudflare integration for edge security
- **DNS Filtering** - Pi-hole integration for ad-blocking and malware protection
- **Threat Detection** - Real-time security event monitoring
- **IP Sanitization** - All IPs displayed in X.X format for security

### Infrastructure Components
- **Palo Alto PA-220** - Enterprise firewall (Mom's basement)
- **UniFi Dream Machine** - Network management (network closet)
- **Raspberry Pi Cluster** - DNS filtering and monitoring (behind the TV)
- **Cloudflare Workers** - Edge computing and CDN

## 🛠️ Tech Stack

- **Frontend:** Vanilla JavaScript with JetBrains Mono font
- **Backend:** Node.js API with Express
- **Infrastructure:** Docker, GitHub Actions CI/CD
- **Security:** Cloudflare Zero-Trust, Pi-hole DNS
- **Monitoring:** Custom service health checks

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/jag18729/vandine-network-monitor.git
cd vandine-network-monitor

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start with Docker
docker-compose up -d

# Or start locally
npm start
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run linting
npm run lint

# Type checking
npm run typecheck
```

## 🚢 Deployment

### GitHub Actions CI/CD

The project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline** - Runs on every push and PR
- **Security Scanning** - Automated vulnerability detection
- **Auto-deployment** - Deploys to production on main branch

### Manual Deployment

```bash
# Deploy to production
./deploy.sh

# Deploy with Docker
docker-compose -f docker-compose.yml up -d
```

## 📊 API Documentation

### Health Check Endpoint
```http
GET /api/health
```

### Services Status
```http
GET /api/services
```

### Cloudflare Analytics
```http
GET /api/cloudflare/analytics
```

### Pi-hole Statistics
```http
GET /api/pihole/stats
```

## 🔒 Security

- All sensitive data is stored in environment variables
- IP addresses are sanitized in the UI (X.X format)
- Zero-Trust security model with Cloudflare
- Regular security audits via GitHub Actions

## 🎯 Performance

- **Uptime:** 99.97% (0.03% downtime was Mom vacuuming)
- **Response Time:** <50ms average
- **Lighthouse Score:** 98/100
- **Load Time:** <1s on 3G connection

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👨‍💻 Author

**John Marston** - Network Security Engineer

## 🏆 Achievements

- Successfully monitoring Mom's entire home network
- Zero security breaches (except when Mom clicks suspicious links)
- 99.97% uptime maintained
- Featured in "Homelab Heroes" magazine (Mom's fridge door)

---

Built with ❤️ and lots of ☕ from Mom's house
EOFMARKER'
