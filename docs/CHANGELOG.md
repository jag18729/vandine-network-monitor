# Changelog

All notable changes to the Vandine NOC project.

## [2026-01-14] - Major Dashboard Overhaul

### Dashboard UI Enhancements
- **Glassmorphism Design** - Modern frosted glass effects with backdrop blur
- **Animated Background** - Subtle gradient shifts (15s cycle) with floating particles
- **Grid Overlay** - Tech-inspired 50px grid pattern for NOC aesthetic
- **Glowing Status Indicators** - Pulse animations for online/offline/warning states
- **Enhanced Hover Effects** - 3D transforms, ripple effects on buttons
- **Custom Scrollbars** - Gradient-styled scrollbars matching theme

### Typography & Layout
- **JetBrains Mono** - Set as primary font throughout dashboard
- **Responsive Design** - Mobile breakpoints at 768px
- **Compact Header** - Moved tagline to footer for cleaner top section
- **Improved Spacing** - Consistent padding and margins throughout

### SNMP Monitoring
- **SNMPv3 Integration** - Secure monitoring with SHA+AES authentication
- **UDM Pro Metrics** - 59 interfaces monitored in real-time
- **SNMP Monitor Tab** - Dedicated page with:
  - Connection status banner
  - Device cards with traffic summary
  - Filterable interface table
  - Top interfaces by traffic
  - PromQL query console

### Cloudflare Integration
- **Edge Detection Fix** - Changed from cross-origin to same-origin `/cdn-cgi/trace`
- **Bot Fight Mode Documentation** - Troubleshooting guide for 403 errors
- **Argo Tunnel Setup** - Full documentation for secure access

### Nginx Configuration
- **Portfolio Site** - Added `/reveal/` path serving React app
- **Asset Routing** - Fixed absolute paths for React app assets
- **Reverse Proxy Locations** - Documented all proxy endpoints

### CI/CD Pipeline Fixes
- **Dependency Conflict Resolved** - Updated django-celery-beat 2.5.0 → 2.6.0
- **Workflow Simplification** - Added continue-on-error for optional steps
- **Conditional Checks** - Skip steps if files don't exist
- **Branch Reference Fix** - Removed non-existent dev branch from auto-update

### Dependabot Integration
- **Automatic Updates** - Weekly dependency checks
- **Grouped Dependencies** - Django, Celery, Testing packages grouped
- **Multi-Ecosystem** - Python (pip), GitHub Actions, Docker, npm

### Documentation
Created comprehensive `/docs/` directory:
- `ARCHITECTURE.md` - System topology and service dependencies
- `SNMP_MONITORING.md` - SNMPv3 setup and PromQL queries
- `NGINX_CONFIGURATION.md` - Reverse proxy and SSL setup
- `CLOUDFLARE_SETUP.md` - Tunnel, DNS, and security settings
- `DASHBOARD_FEATURES.md` - UI components and animations
- `DEPLOYMENT.md` - Full deployment and CI/CD guide
- `TROUBLESHOOTING.md` - Common issues and recovery
- `API_REFERENCE.md` - All endpoints and examples

### Claude Code Skills
Added custom skills in `.claude/commands/`:
- `/check-snmp` - Test SNMP exporter and metrics
- `/check-nginx` - Validate nginx configuration
- `/check-cloudflare` - DNS and security diagnostics
- `/check-services` - All service health checks
- `/sync-site` - Pull site from pi1 to local repo

### README Updates
- Added recent updates section
- Documented all dashboard pages
- Created API endpoints table
- Added Future Enhancements roadmap
- Updated network topology diagram

---

## [2026-01-13] - Initial Enhanced Dashboards

### Added
- Route Testing tab with Cloudflare/Direct/IPsec comparison
- DNS Dashboard with DoH API integration
- NASA Principles page
- Quick links grid to all monitoring services
- Enhanced performance comparison tables

### Infrastructure
- GitHub Actions CI/CD pipeline
- Docker containerization setup
- Prometheus + Grafana monitoring stack

---

## Version History

| Date | Version | Description |
|------|---------|-------------|
| 2026-01-14 | 2.0.0 | Major UI overhaul, SNMP monitoring, documentation |
| 2026-01-13 | 1.1.0 | Enhanced dashboards, route testing |
| 2026-01-13 | 1.0.0 | Initial release with CI/CD |
