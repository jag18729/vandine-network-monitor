#!/usr/bin/env python3
"""
API Gateway Agent - Intelligent routing and task management
Provides a unified API for all agent operations with smart routing
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx
import asyncio
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vandine API Gateway Agent", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
WORKER_URL = "http://localhost:8787"
PI_EXECUTOR_URL = "http://localhost:8000"
CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"

class TaskType(str, Enum):
    DNS_UPDATE = "dns_update"
    CACHE_PURGE = "cache_purge"
    SSL_CHECK = "ssl_check"
    FIREWALL_RULE = "firewall_rule"
    RATE_LIMIT = "rate_limit"
    WORKER_DEPLOY = "worker_deploy"
    ANALYTICS_QUERY = "analytics_query"
    HEALTH_CHECK = "health_check"
    SYSTEM_METRIC = "system_metric"
    BACKUP = "backup"
    SECURITY_SCAN = "security_scan"

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskRequest(BaseModel):
    type: TaskType
    priority: Priority = Priority.MEDIUM
    data: Dict[str, Any]
    schedule: Optional[str] = None  # Cron expression for scheduled tasks
    retry_count: int = 3
    timeout: int = 300  # seconds

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None

class GatewayStatus(BaseModel):
    status: str
    uptime: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    services: Dict[str, str]
    last_health_check: datetime

# In-memory task store (in production, use Redis or database)
task_store = {}
task_metrics = {
    "total": 0,
    "completed": 0,
    "failed": 0,
    "by_type": {}
}

async def route_task(task: TaskRequest) -> Dict[str, Any]:
    """
    Intelligently route tasks to appropriate service
    """
    # DNS, Cache, SSL, Firewall tasks go to Cloudflare
    if task.type in [TaskType.DNS_UPDATE, TaskType.CACHE_PURGE, 
                     TaskType.SSL_CHECK, TaskType.FIREWALL_RULE]:
        return await execute_cloudflare_task(task)
    
    # System metrics and health checks go to Pi Executor
    elif task.type in [TaskType.SYSTEM_METRIC, TaskType.HEALTH_CHECK]:
        return await execute_pi_task(task)
    
    # Worker deployment and analytics can go through Worker
    elif task.type in [TaskType.WORKER_DEPLOY, TaskType.ANALYTICS_QUERY]:
        return await execute_worker_task(task)
    
    # Security scans and backups are hybrid
    elif task.type in [TaskType.SECURITY_SCAN, TaskType.BACKUP]:
        return await execute_hybrid_task(task)
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown task type: {task.type}")

async def execute_cloudflare_task(task: TaskRequest) -> Dict[str, Any]:
    """Execute Cloudflare-related tasks"""
    logger.info(f"Executing Cloudflare task: {task.type}")
    
    # Simulate Cloudflare API calls
    result = {
        "service": "cloudflare",
        "task_type": task.type,
        "status": "success",
        "data": {}
    }
    
    if task.type == TaskType.DNS_UPDATE:
        result["data"] = {
            "record": task.data.get("record"),
            "type": task.data.get("type", "A"),
            "content": task.data.get("content"),
            "updated_at": datetime.now().isoformat()
        }
    elif task.type == TaskType.CACHE_PURGE:
        result["data"] = {
            "purged_urls": task.data.get("urls", []),
            "purge_everything": task.data.get("purge_everything", False),
            "purged_at": datetime.now().isoformat()
        }
    
    return result

async def execute_pi_task(task: TaskRequest) -> Dict[str, Any]:
    """Execute Pi Executor tasks"""
    logger.info(f"Executing Pi task: {task.type}")
    
    async with httpx.AsyncClient() as client:
        try:
            if task.type == TaskType.HEALTH_CHECK:
                response = await client.get(f"{PI_EXECUTOR_URL}/health")
                return response.json()
            elif task.type == TaskType.SYSTEM_METRIC:
                response = await client.get(f"{PI_EXECUTOR_URL}/metrics")
                return response.json()
        except Exception as e:
            logger.error(f"Pi task failed: {e}")
            return {"status": "error", "message": str(e)}

async def execute_worker_task(task: TaskRequest) -> Dict[str, Any]:
    """Execute Worker-based tasks"""
    logger.info(f"Executing Worker task: {task.type}")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": "Bearer secret_auth_token_123"}
            response = await client.post(
                f"{WORKER_URL}/tasks",
                json={
                    "type": task.type,
                    "priority": task.priority,
                    "data": task.data
                },
                headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"Worker task failed: {e}")
            return {"status": "error", "message": str(e)}

async def execute_hybrid_task(task: TaskRequest) -> Dict[str, Any]:
    """Execute tasks requiring multiple services"""
    logger.info(f"Executing hybrid task: {task.type}")
    
    results = {}
    
    if task.type == TaskType.SECURITY_SCAN:
        # Get system info from Pi
        pi_result = await execute_pi_task(
            TaskRequest(type=TaskType.SYSTEM_METRIC, priority=task.priority, data={})
        )
        results["system"] = pi_result
        
        # Check Cloudflare security settings
        cf_result = await execute_cloudflare_task(
            TaskRequest(type=TaskType.FIREWALL_RULE, priority=task.priority, 
                       data={"action": "list"})
        )
        results["cloudflare"] = cf_result
    
    return results

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
    """
    Create a new task with intelligent routing
    """
    import uuid
    task_id = str(uuid.uuid4())
    
    # Store task
    task_store[task_id] = {
        "id": task_id,
        "request": task.dict(),
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "result": None
    }
    
    # Update metrics
    task_metrics["total"] += 1
    task_metrics["by_type"][task.type] = task_metrics["by_type"].get(task.type, 0) + 1
    
    # Execute task in background
    background_tasks.add_task(process_task, task_id, task)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message=f"Task {task.type} queued for processing",
        created_at=datetime.now(),
        estimated_completion=datetime.now() + timedelta(seconds=task.timeout)
    )

async def process_task(task_id: str, task: TaskRequest):
    """Process task asynchronously"""
    try:
        task_store[task_id]["status"] = "processing"
        task_store[task_id]["updated_at"] = datetime.now()
        
        result = await route_task(task)
        
        task_store[task_id]["status"] = "completed"
        task_store[task_id]["result"] = result
        task_store[task_id]["updated_at"] = datetime.now()
        task_metrics["completed"] += 1
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_store[task_id]["status"] = "failed"
        task_store[task_id]["error"] = str(e)
        task_store[task_id]["updated_at"] = datetime.now()
        task_metrics["failed"] += 1

@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status and result"""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_store[task_id]

@app.get("/api/v1/status", response_model=GatewayStatus)
async def get_gateway_status():
    """Get API Gateway status"""
    import time
    
    # Check service health
    services = {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Check Worker
            try:
                response = await client.get(f"{WORKER_URL}/health", timeout=2)
                services["worker"] = "online" if response.status_code == 200 else "offline"
            except:
                services["worker"] = "offline"
            
            # Check Pi Executor
            try:
                response = await client.get(f"{PI_EXECUTOR_URL}/health", timeout=2)
                services["pi_executor"] = "online" if response.status_code == 200 else "offline"
            except:
                services["pi_executor"] = "offline"
    except:
        pass
    
    active_tasks = sum(1 for t in task_store.values() 
                      if t["status"] in ["pending", "processing"])
    
    return GatewayStatus(
        status="operational",
        uptime=time.time(),
        active_tasks=active_tasks,
        completed_tasks=task_metrics["completed"],
        failed_tasks=task_metrics["failed"],
        services=services,
        last_health_check=datetime.now()
    )

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get detailed metrics"""
    return {
        "task_metrics": task_metrics,
        "task_types": list(TaskType),
        "priorities": list(Priority),
        "active_tasks": [
            {"id": tid, "type": t["request"]["type"], "status": t["status"]}
            for tid, t in task_store.items()
            if t["status"] in ["pending", "processing"]
        ]
    }

@app.get("/api/v1/capabilities")
async def get_capabilities():
    """List all available capabilities"""
    return {
        "task_types": [
            {
                "type": task_type.value,
                "description": get_task_description(task_type),
                "service": get_task_service(task_type)
            }
            for task_type in TaskType
        ],
        "priorities": [p.value for p in Priority],
        "services": ["cloudflare", "pi_executor", "worker", "hybrid"],
        "features": [
            "Intelligent task routing",
            "Priority-based execution",
            "Retry mechanism",
            "Scheduled tasks",
            "Real-time monitoring",
            "Multi-service orchestration"
        ]
    }

def get_task_description(task_type: TaskType) -> str:
    descriptions = {
        TaskType.DNS_UPDATE: "Update DNS records in Cloudflare",
        TaskType.CACHE_PURGE: "Purge CDN cache",
        TaskType.SSL_CHECK: "Verify SSL certificate status",
        TaskType.FIREWALL_RULE: "Manage firewall rules",
        TaskType.RATE_LIMIT: "Configure rate limiting",
        TaskType.WORKER_DEPLOY: "Deploy Cloudflare Workers",
        TaskType.ANALYTICS_QUERY: "Query analytics data",
        TaskType.HEALTH_CHECK: "System health check",
        TaskType.SYSTEM_METRIC: "Collect system metrics",
        TaskType.BACKUP: "Perform backup operations",
        TaskType.SECURITY_SCAN: "Run security scan"
    }
    return descriptions.get(task_type, "Unknown task type")

def get_task_service(task_type: TaskType) -> str:
    service_map = {
        TaskType.DNS_UPDATE: "cloudflare",
        TaskType.CACHE_PURGE: "cloudflare",
        TaskType.SSL_CHECK: "cloudflare",
        TaskType.FIREWALL_RULE: "cloudflare",
        TaskType.RATE_LIMIT: "cloudflare",
        TaskType.WORKER_DEPLOY: "worker",
        TaskType.ANALYTICS_QUERY: "worker",
        TaskType.HEALTH_CHECK: "pi_executor",
        TaskType.SYSTEM_METRIC: "pi_executor",
        TaskType.BACKUP: "hybrid",
        TaskType.SECURITY_SCAN: "hybrid"
    }
    return service_map.get(task_type, "unknown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
