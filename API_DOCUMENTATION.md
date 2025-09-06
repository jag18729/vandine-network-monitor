# Vandine Network Monitor API Documentation

## Base URLs

- API Gateway: http://192.168.2.7:8888/api/v1
- Pi Executor: http://192.168.2.7:8000  
- Worker Simulator: http://192.168.2.7:8787

## Authentication

Most endpoints require Bearer token authentication:

    Authorization: Bearer secret_auth_token_123

## API Gateway Endpoints

### 1. Create Task
POST /api/v1/tasks

Creates a new task with intelligent routing.

#### Request Body
    {
      "type": "dns_update",
      "priority": "high",
      "data": {
        "record": "api.vandine.us",
        "type": "A",
        "content": "192.168.1.100"
      },
      "retry_count": 3,
      "timeout": 300
    }

#### Response
    {
      "task_id": "df182569-da9d-4327-8f0f-2a51f91b965d",
      "status": "pending",
      "message": "Task dns_update queued for processing",
      "created_at": "2025-09-06T19:56:36.278349",
      "estimated_completion": "2025-09-06T20:01:36.278365"
    }

### 2. Get Task Status
GET /api/v1/tasks/{task_id}

Retrieves status and result of a specific task.

### 3. Gateway Status
GET /api/v1/status

Returns overall gateway and service health.

### 4. Get Capabilities
GET /api/v1/capabilities

Lists all available task types and features.

### 5. Get Metrics
GET /api/v1/metrics

Returns detailed task and performance metrics.

## Pi Executor Endpoints

### 1. Health Check
GET /health

No authentication required.

### 2. System Metrics
GET /metrics

Returns system resource utilization.

### 3. Execute Command
POST /execute

Executes system commands (restricted).

## Task Types Reference

### DNS Management
    {
      "type": "dns_update",
      "data": {
        "record": "subdomain.example.com",
        "type": "A",
        "content": "192.168.1.1",
        "ttl": 3600,
        "proxied": true
      }
    }

### Cache Operations
    {
      "type": "cache_purge",
      "data": {
        "urls": [
          "https://example.com/path1",
          "https://example.com/path2"
        ],
        "purge_everything": false
      }
    }

### SSL Certificate Check
    {
      "type": "ssl_check",
      "data": {
        "domains": ["example.com", "www.example.com"],
        "check_expiry": true,
        "alert_days": 30
      }
    }

### Firewall Rules
    {
      "type": "firewall_rule",
      "data": {
        "action": "create",
        "expression": "ip.src eq 192.168.1.0/24",
        "action_type": "allow",
        "description": "Allow local network"
      }
    }

### Health Check
    {
      "type": "health_check",
      "data": {
        "services": ["nginx", "docker", "agent"],
        "include_metrics": true
      }
    }

## Error Responses

### 400 Bad Request
    {
      "error": "Invalid task type",
      "detail": "Task type 'invalid_type' is not recognized",
      "status_code": 400
    }

### 401 Unauthorized
    {
      "error": "Unauthorized",
      "detail": "Invalid or missing authentication token",
      "status_code": 401
    }

### 404 Not Found
    {
      "error": "Task not found",
      "detail": "Task with ID 'abc123' does not exist",
      "status_code": 404
    }

### 500 Internal Server Error
    {
      "error": "Internal server error",
      "detail": "An unexpected error occurred",
      "status_code": 500
    }

## Rate Limiting

- Default Rate Limit: 100 requests per minute per IP
- Burst Limit: 20 requests
- Headers Returned:
  - X-RateLimit-Limit: Maximum requests allowed
  - X-RateLimit-Remaining: Requests remaining
  - X-RateLimit-Reset: Unix timestamp when limit resets

## Python Client Example

    import httpx

    class VandineClient:
        def __init__(self, base_url, token):
            self.base_url = base_url
            self.headers = {"Authorization": f"Bearer {token}"}
        
        async def create_task(self, task_type, data, priority="medium"):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/tasks",
                    json={
                        "type": task_type,
                        "priority": priority,
                        "data": data
                    },
                    headers=self.headers
                )
                return response.json()

## cURL Examples

#### Create DNS Update Task
    curl -X POST http://192.168.2.7:8888/api/v1/tasks \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer secret_auth_token_123" \
      -d '{
        "type": "dns_update",
        "priority": "high",
        "data": {
          "record": "test.vandine.us",
          "type": "A",
          "content": "192.168.1.50"
        }
      }'

#### Check System Health
    curl http://192.168.2.7:8000/health

#### Get Gateway Status
    curl http://192.168.2.7:8888/api/v1/status

## API Versioning

- Current Version: v1
- Version in URL: /api/v1/
- Deprecation Notice: 6 months before sunset
- Backward Compatibility: 2 major versions

## Support

- GitHub Issues: https://github.com/jag18729/vandine-network-monitor/issues
- Documentation: This file
- Response Time: Best effort

---
Last Updated: Sep 6, 2025
API Version: 1.0.0
