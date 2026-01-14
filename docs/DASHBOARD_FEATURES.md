# NOC Dashboard Features

## Overview

The Vandine NOC Dashboard is a single-page application providing real-time monitoring and management of network infrastructure.

## Visual Design

### Glassmorphism UI
- Frosted glass effect with `backdrop-filter: blur()`
- Transparent backgrounds with rgba colors
- Glowing borders and shadows
- Smooth animations and transitions

### Color Scheme
| Color | Hex | Usage |
|-------|-----|-------|
| Cyan | #00d4ff | Primary accent, links, highlights |
| Green | #10b981 | Online status, success |
| Red | #ef4444 | Offline status, errors |
| Yellow | #f59e0b | Warning status |
| Purple | #6366f1 | Secondary buttons |
| Background | #0a0e27 | Dark navy background |

### Typography
- **Font**: JetBrains Mono (monospace)
- **Base Size**: 15px
- **Line Height**: 1.7
- **Title**: 1.8rem
- **Headings**: 1.5rem
- **Body**: 0.95rem

## Dashboard Pages

### 1. Infrastructure
Main overview with device cards showing:
- Palo Alto PA-220 status
- Cloudflare Edge location
- UniFi Dream Machine stats
- Raspberry Pi cluster health

### 2. Palo Alto PA-220
Firewall monitoring:
- Active sessions
- Threat prevention stats
- Policy hit counts
- System resources

### 3. Cloudflare Edge
CDN and security:
- Edge location detection
- Latency measurement
- Cache hit rate
- DDoS blocked count
- WAF events

### 4. Route Testing
Performance comparison:
- Cloudflare Argo route
- Direct ISP route
- IPsec tunnel route
- Latency and throughput metrics

### 5. UniFi Dream Machine
Router management:
- Connected clients
- Traffic statistics
- Interface status
- Port utilization

### 6. Raspberry Pi Cluster
Service health:
- Pi-hole DNS stats
- Docker container status
- System resources (CPU, RAM, disk)
- Service uptime

### 7. Zero Trust
Security posture:
- Trust level indicators
- Authentication status
- Network segmentation
- Access policies

### 8. Automation
Self-healing status:
- Automated remediation logs
- Scheduled tasks
- Event history
- Action triggers

### 9. SNMP Monitor
Network interface monitoring:
- Real-time traffic graphs
- Interface status table
- Top interfaces by traffic
- Error and discard rates
- PromQL query console

## Quick Links

Grid of service shortcuts:
| Icon | Service | URL |
|------|---------|-----|
| 🚀 | NASA Principles | /nasa.html |
| 🌐 | DNS Dashboard | /dns-dashboard.html |
| 🔬 | Network Lab | /network-test.html |
| ⚙️ | DevOps Center | /devops.html |
| 🤖 | Agent Dashboard | /agent-dashboard.html |
| 👤 | Reveal.me | /reveal/ |
| 📊 | Grafana | /grafana/ |
| 📈 | Prometheus | /prometheus/ |
| 🛡️ | Pi-hole Admin | /pihole/ |
| 🔔 | Alertmanager | /alertmanager/ |
| 🎯 | Blackbox | /blackbox/ |
| 📡 | SNMP Monitor | (tab) |
| 💻 | Node Exporter | /node-metrics/ |

## Interactive Features

### Auto-Detection
- **Cloudflare Edge**: Fetches `/cdn-cgi/trace` on page load
- **Latency**: Measures round-trip time to edge

### Real-Time Updates
- Pi-hole blocked count
- Interface traffic rates
- Service status checks

### API Integration
```javascript
const API_BASE = 'http://192.168.2.70:8887';
const PIHOLE_API = 'http://192.168.2.70:8889';
const PROMETHEUS_API = '/prometheus/api/v1';
```

## SNMP Monitor Tab

### Features
1. **Connection Status Banner**
   - Shows device and interface count
   - Real-time update indicator

2. **Device Cards**
   - UDM Pro status
   - Interface summary
   - Traffic totals

3. **Traffic Summary**
   - Total in/out bytes
   - Active interfaces
   - Error counts

4. **Top Interfaces**
   - Ranked by traffic
   - Color-coded status

5. **Interface Table**
   - Sortable columns
   - Filterable by status
   - Search functionality

6. **Query Console**
   - Direct PromQL queries
   - Formatted results

### Filter Buttons
- **All**: Show all interfaces
- **Up**: Only operational interfaces
- **Down**: Non-operational interfaces
- **Errors**: Interfaces with errors

## CSS Animations

### Background Effects
```css
/* Gradient shift */
animation: gradientShift 15s ease infinite;

/* Floating particles */
animation: particleFloat 20s linear infinite;

/* Grid overlay */
background-size: 50px 50px;
```

### Status Indicators
```css
/* Online pulse */
animation: statusGlow 2s ease-in-out infinite;

/* Offline blink */
animation: statusPulse 1s ease-in-out infinite;

/* Warning flash */
animation: warningBlink 1.5s ease-in-out infinite;
```

### Hover Effects
```css
/* Card hover */
transform: translateY(-8px) scale(1.01);
box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);

/* Button ripple */
animation: ripple 0.6s;
```

## Responsive Design

### Breakpoints
- **Desktop**: > 768px (full layout)
- **Tablet**: 768px (condensed)
- **Mobile**: < 768px (stacked)

### Mobile Adjustments
```css
@media (max-width: 768px) {
    h1 { font-size: 1.6rem; }
    .container { padding: 1.5rem 1rem; }
    .healing-status { display: none; }
}
```

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

### Required Features
- CSS Grid
- Flexbox
- CSS Variables
- backdrop-filter
- CSS Animations
