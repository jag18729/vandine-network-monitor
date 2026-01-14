# API Reference

## Overview

The Vandine NOC exposes several APIs for monitoring and management.

## Base URLs

| Service | Internal URL | External URL |
|---------|--------------|--------------|
| API Gateway | http://localhost:8887 | https://vandine.us/api |
| Pi-hole API | http://localhost:8889 | (internal only) |
| Prometheus | http://localhost:9090 | https://vandine.us/prometheus |
| SNMP Exporter | http://localhost:9116 | https://vandine.us/snmp |

## API Gateway Endpoints

### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-14T00:00:00Z"
}
```

### Service Status
```http
GET /api/status
```

**Response**:
```json
{
  "services": {
    "nginx": "running",
    "prometheus": "running",
    "grafana": "running"
  }
}
```

## Pi-hole API

### Summary Statistics
```http
GET /api/pihole/summary
```

**Response**:
```json
{
  "domains_being_blocked": 123456,
  "dns_queries_today": 50000,
  "ads_blocked_today": 5000,
  "ads_percentage_today": 10.0,
  "unique_domains": 1000,
  "queries_forwarded": 45000,
  "queries_cached": 4500,
  "status": "enabled"
}
```

### Query Types
```http
GET /api/pihole/querytypes
```

### Top Domains
```http
GET /api/pihole/topDomains
```

### Top Advertisers
```http
GET /api/pihole/topAds
```

## Prometheus API

### Instant Query
```http
GET /prometheus/api/v1/query
```

**Parameters**:
| Param | Type | Description |
|-------|------|-------------|
| query | string | PromQL query |
| time | string | Evaluation timestamp (optional) |

**Example**:
```bash
curl -s 'https://vandine.us/prometheus/api/v1/query?query=up'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {"job": "prometheus", "instance": "localhost:9090"},
        "value": [1234567890, "1"]
      }
    ]
  }
}
```

### Range Query
```http
GET /prometheus/api/v1/query_range
```

**Parameters**:
| Param | Type | Description |
|-------|------|-------------|
| query | string | PromQL query |
| start | string | Start timestamp |
| end | string | End timestamp |
| step | string | Query resolution step |

**Example**:
```bash
curl -s 'https://vandine.us/prometheus/api/v1/query_range?query=rate(ifHCInOctets[5m])&start=2026-01-14T00:00:00Z&end=2026-01-14T01:00:00Z&step=60s'
```

### Targets
```http
GET /prometheus/api/v1/targets
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "activeTargets": [
      {
        "job": "snmp-udm",
        "instance": "192.168.2.1",
        "health": "up",
        "lastScrape": "2026-01-14T00:00:00Z"
      }
    ]
  }
}
```

### Alerting Rules
```http
GET /prometheus/api/v1/rules
```

### Alerts
```http
GET /prometheus/api/v1/alerts
```

## SNMP Exporter API

### Scrape Target
```http
GET /snmp/snmp
```

**Parameters**:
| Param | Type | Description |
|-------|------|-------------|
| target | string | SNMP target IP |
| module | string | SNMP module (e.g., if_mib) |

**Example**:
```bash
curl -s 'https://vandine.us/snmp/snmp?target=192.168.2.1&module=if_mib'
```

**Response** (Prometheus format):
```
# HELP ifHCInOctets The total number of octets received on the interface
# TYPE ifHCInOctets counter
ifHCInOctets{ifDescr="eth0",ifIndex="1"} 1234567890
ifHCInOctets{ifDescr="eth1",ifIndex="2"} 9876543210
```

### Metrics
```http
GET /snmp/metrics
```

Returns internal SNMP exporter metrics.

## Cloudflare Trace

### Edge Detection
```http
GET /cdn-cgi/trace
```

**Response** (text):
```
fl=123abc
h=vandine.us
ip=1.2.3.4
ts=1234567890.123
visit_scheme=https
uag=Mozilla/5.0...
colo=LAX
sliver=none
http=http/2
loc=US
tls=TLSv1.3
sni=plaintext
warp=off
gateway=off
```

## Common PromQL Queries

### Interface Traffic
```promql
# Input rate (bytes/sec)
rate(ifHCInOctets{instance="192.168.2.1"}[5m])

# Output rate (bytes/sec)
rate(ifHCOutOctets{instance="192.168.2.1"}[5m])

# Total throughput
sum(rate(ifHCInOctets[5m]) + rate(ifHCOutOctets[5m]))
```

### Top Interfaces
```promql
# Top 10 by traffic
topk(10, rate(ifHCInOctets[5m]) + rate(ifHCOutOctets[5m]))

# Top 5 by errors
topk(5, rate(ifInErrors[5m]) + rate(ifOutErrors[5m]))
```

### Interface Status
```promql
# All up interfaces
ifOperStatus == 1

# All down interfaces
ifOperStatus == 2

# Interface count by status
count by (ifOperStatus) (ifOperStatus)
```

### System Metrics
```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Disk usage
(1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (invalid query) |
| 401 | Unauthorized |
| 403 | Forbidden (Cloudflare challenge) |
| 404 | Not found |
| 500 | Internal server error |
| 502 | Bad gateway (backend down) |
| 503 | Service unavailable |
| 504 | Gateway timeout |

## Rate Limits

| Service | Limit |
|---------|-------|
| Prometheus | No limit (internal) |
| SNMP Exporter | Scrape interval: 15s |
| Pi-hole API | No limit (internal) |
| Cloudflare | Based on plan |

## Authentication

Most internal APIs do not require authentication. For Grafana:

```http
Authorization: Bearer <api_key>
```

Or basic auth:
```http
Authorization: Basic <base64(user:pass)>
```

## CORS

Cross-origin requests are handled by Cloudflare. Internal APIs allow all origins for dashboard access.

## WebSocket

### Connection
```javascript
const ws = new WebSocket('wss://vandine.us/ws/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Message Format
```json
{
  "type": "metric_update",
  "data": {
    "timestamp": "2026-01-14T00:00:00Z",
    "metrics": {}
  }
}
```
