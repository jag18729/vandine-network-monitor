# SNMP Monitoring Setup

## Overview

The Vandine NOC uses SNMPv3 to monitor the UniFi Dream Machine Pro, collecting interface metrics for traffic analysis and health monitoring.

## SNMPv3 Configuration

### Security Settings
- **Security Level**: authPriv (authentication + encryption)
- **Authentication Protocol**: SHA
- **Privacy Protocol**: AES
- **Username**: Configured in UDM Pro and snmp.yml

### UDM Pro Setup

1. SSH into UDM Pro:
   ```bash
   ssh root@192.168.2.1
   ```

2. Edit SNMP configuration:
   ```bash
   vi /etc/snmp/snmpd.conf
   ```

3. Add SNMPv3 user:
   ```
   createUser snmpuser SHA "authpassword" AES "privpassword"
   rouser snmpuser priv
   ```

4. Restart SNMP daemon:
   ```bash
   systemctl restart snmpd
   ```

## SNMP Exporter Configuration

### Location
```
/etc/snmp_exporter/snmp.yml
```

### Module Configuration
```yaml
if_mib:
  version: 3
  auth:
    security_level: authPriv
    username: snmpuser
    password: authpassword
    auth_protocol: SHA
    priv_protocol: AES
    priv_password: privpassword
  walk:
    - 1.3.6.1.2.1.2      # interfaces
    - 1.3.6.1.2.1.31.1   # ifXTable (64-bit counters)
  metrics:
    - name: ifHCInOctets
      oid: 1.3.6.1.2.1.31.1.1.1.6
      type: counter
      indexes:
        - labelname: ifIndex
          type: Integer
      lookups:
        - labels: [ifIndex]
          labelname: ifDescr
          oid: 1.3.6.1.2.1.2.2.1.2
          type: DisplayString
    - name: ifHCOutOctets
      oid: 1.3.6.1.2.1.31.1.1.1.10
      type: counter
    - name: ifOperStatus
      oid: 1.3.6.1.2.1.2.2.1.8
      type: gauge
```

## Prometheus Scrape Configuration

### Location
```
/etc/prometheus/prometheus.yml
```

### Job Configuration
```yaml
scrape_configs:
  - job_name: 'snmp-udm'
    static_configs:
      - targets:
        - 192.168.2.1  # UDM Pro
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9116  # SNMP exporter address
```

## Metrics Reference

### Interface Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `ifHCInOctets` | Counter | Total bytes received (64-bit) |
| `ifHCOutOctets` | Counter | Total bytes transmitted (64-bit) |
| `ifOperStatus` | Gauge | Interface status (1=up, 2=down, 3=testing) |
| `ifAdminStatus` | Gauge | Admin status (1=up, 2=down) |
| `ifSpeed` | Gauge | Interface speed in bps |
| `ifHighSpeed` | Gauge | Interface speed in Mbps |
| `ifDescr` | Label | Interface description |
| `ifAlias` | Label | Interface alias/name |

### Common PromQL Queries

**Interface Traffic Rate (bytes/sec)**
```promql
rate(ifHCInOctets{instance="192.168.2.1"}[5m])
```

**Top 10 Interfaces by Traffic**
```promql
topk(10, rate(ifHCInOctets[5m]) + rate(ifHCOutOctets[5m]))
```

**Interface Status**
```promql
ifOperStatus{instance="192.168.2.1"} == 1
```

**Total Network Throughput**
```promql
sum(rate(ifHCInOctets{instance="192.168.2.1"}[5m])) + sum(rate(ifHCOutOctets{instance="192.168.2.1"}[5m]))
```

**Interface Error Rate**
```promql
rate(ifInErrors[5m]) + rate(ifOutErrors[5m])
```

## Troubleshooting

### Test SNMP Connectivity
```bash
# From Pi-1
snmpwalk -v3 -l authPriv -u snmpuser -a SHA -A "authpassword" -x AES -X "privpassword" 192.168.2.1 1.3.6.1.2.1.1.1.0
```

### Test SNMP Exporter
```bash
curl -s 'http://localhost:9116/snmp?target=192.168.2.1&module=if_mib' | head -50
```

### Check Prometheus Targets
```bash
curl -s 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | select(.job=="snmp-udm")'
```

### Verify Metrics in Prometheus
```bash
curl -s 'http://localhost:9090/api/v1/query?query=ifHCInOctets' | jq '.data.result | length'
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No metrics | SNMP timeout | Check firewall, verify credentials |
| Auth errors | Wrong password | Verify SHA/AES passwords match |
| Missing interfaces | OID not walked | Add OID to walk list in snmp.yml |
| Counter resets | 32-bit overflow | Use ifHC* (64-bit) counters |

## Service Management

### Restart SNMP Exporter
```bash
sudo systemctl restart snmp_exporter
```

### Check Logs
```bash
journalctl -u snmp_exporter -f
```

### Reload Prometheus
```bash
sudo systemctl reload prometheus
```

## UDM Pro Interfaces

The UDM Pro typically exposes 59+ interfaces:

| Interface | Description |
|-----------|-------------|
| eth0-eth7 | LAN ports |
| eth8 | WAN1 (Primary) |
| eth9 | WAN2/SFP+ |
| br* | Bridge interfaces |
| vlan* | VLAN interfaces |
| tun* | VPN tunnels |
| ipsec* | IPsec tunnels |
