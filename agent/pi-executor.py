#!/usr/bin/env python3
"""
Raspberry Pi Task Executor
Works with Cloudflare Worker agent to execute local tasks
"""

import json
import time
import subprocess
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# Configuration
CLOUDFLARE_WORKER_URL = "https://network-agent.YOUR_SUBDOMAIN.workers.dev"
LOCAL_API_PORT = 8000
LOG_FILE = "agent.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Network Agent Executor", version="1.0.0")

# Request models
class Task(BaseModel):
    id: str
    type: str
    priority: str
    action: str
    parameters: Dict[str, Any] = {}

class ServiceAction(BaseModel):
    service: str
    action: str  # start, stop, restart, status

class DeploymentRequest(BaseModel):
    branch: str
    environment: str  # dev, staging, production

# Task executor class
class TaskExecutor:
    def __init__(self):
        self.tasks_executed = 0
        self.last_execution = None
        
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task based on type"""
        logger.info(f"Executing task: {task.id} - Type: {task.type}")
        
        try:
            if task.type == "monitor":
                return await self.monitor_infrastructure()
            elif task.type == "deploy":
                return await self.deploy_application(task.parameters)
            elif task.type == "backup":
                return await self.create_backup()
            elif task.type == "remediate":
                return await self.auto_remediate(task.parameters)
            elif task.type == "security_scan":
                return await self.security_scan()
            elif task.type == "performance_test":
                return await self.performance_test()
            else:
                return {"status": "error", "message": f"Unknown task type: {task.type}"}
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def monitor_infrastructure(self) -> Dict[str, Any]:
        """Monitor local infrastructure"""
        results = {}
        
        # Check disk usage
        df_output = subprocess.run(['df', '-h'], capture_output=True, text=True)
        results['disk_usage'] = df_output.stdout
        
        # Check memory
        mem_output = subprocess.run(['free', '-h'], capture_output=True, text=True)
        results['memory'] = mem_output.stdout
        
        # Check services
        services = ['nginx', 'docker']
        service_status = {}
        for service in services:
            status = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True, text=True
            )
            service_status[service] = status.stdout.strip()
        results['services'] = service_status
        
        # Check network
        ping_result = subprocess.run(
            ['ping', '-c', '1', '8.8.8.8'],
            capture_output=True, text=True
        )
        results['network'] = 'up' if ping_result.returncode == 0 else 'down'
        
        return {"status": "success", "data": results}
    
    async def deploy_application(self, params: Dict) -> Dict[str, Any]:
        """Deploy application updates"""
        branch = params.get('branch', 'main')
        
        commands = [
            f"cd /home/johnmarston/vandine-network-monitor",
            f"git fetch origin",
            f"git checkout {branch}",
            f"git pull origin {branch}",
            "sudo systemctl reload nginx"
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Deployment failed: {result.stderr}"
                }
        
        return {
            "status": "success",
            "message": f"Deployed {branch} successfully"
        }
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create system backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"/home/johnmarston/backups/backup_{timestamp}"
        
        subprocess.run(f"mkdir -p {backup_dir}", shell=True)
        
        # Backup important directories
        dirs_to_backup = [
            "/home/johnmarston/vandine-network-monitor",
            "/etc/nginx/sites-enabled",
            "/var/www"
        ]
        
        for dir_path in dirs_to_backup:
            if Path(dir_path).exists():
                subprocess.run(
                    f"cp -r {dir_path} {backup_dir}/",
                    shell=True
                )
        
        return {
            "status": "success",
            "message": f"Backup created: {backup_dir}"
        }
    
    async def auto_remediate(self, params: Dict) -> Dict[str, Any]:
        """Auto-remediate issues"""
        issue = params.get('issue')
        
        if issue == 'service_down':
            service = params.get('service')
            subprocess.run(f"sudo systemctl restart {service}", shell=True)
            return {"status": "success", "message": f"Restarted {service}"}
            
        elif issue == 'disk_full':
            # Clean up logs and temp files
            subprocess.run("sudo journalctl --vacuum-time=7d", shell=True)
            subprocess.run("rm -rf /tmp/*", shell=True)
            return {"status": "success", "message": "Cleaned up disk space"}
            
        elif issue == 'high_load':
            # Identify and kill high CPU processes
            result = subprocess.run(
                "ps aux --sort=-pcpu | head -5",
                shell=True, capture_output=True, text=True
            )
            return {"status": "success", "message": "Analyzed high load", "data": result.stdout}
        
        return {"status": "error", "message": "Unknown issue type"}
    
    async def security_scan(self) -> Dict[str, Any]:
        """Run security scan"""
        results = {}
        
        # Check for exposed ports
        netstat = subprocess.run(
            "sudo netstat -tuln",
            shell=True, capture_output=True, text=True
        )
        results['open_ports'] = netstat.stdout
        
        # Check fail2ban
        fail2ban = subprocess.run(
            "sudo fail2ban-client status",
            shell=True, capture_output=True, text=True
        )
        results['fail2ban'] = fail2ban.stdout
        
        # Check for suspicious files
        find_cmd = "find /home -type f -name '*.sh' -mtime -1"
        recent_scripts = subprocess.run(
            find_cmd, shell=True, capture_output=True, text=True
        )
        results['recent_scripts'] = recent_scripts.stdout
        
        return {"status": "success", "data": results}
    
    async def performance_test(self) -> Dict[str, Any]:
        """Run performance test"""
        # Test network speed
        speedtest = subprocess.run(
            "curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -",
            shell=True, capture_output=True, text=True
        )
        
        return {
            "status": "success",
            "data": {
                "speedtest": speedtest.stdout,
                "timestamp": datetime.now().isoformat()
            }
        }

# Initialize executor
executor = TaskExecutor()

# API Endpoints
@app.get("/")
async def root():
    return {
        "name": "Network Agent Pi Executor",
        "version": "1.0.0",
        "status": "operational",
        "tasks_executed": executor.tasks_executed,
        "last_execution": executor.last_execution
    }

@app.post("/execute")
async def execute_task(task: Task, background_tasks: BackgroundTasks):
    """Execute a task from the Cloudflare agent"""
    result = await executor.execute_task(task)
    executor.tasks_executed += 1
    executor.last_execution = datetime.now().isoformat()
    
    # Report back to Cloudflare Worker
    background_tasks.add_task(report_to_cloudflare, task.id, result)
    
    return result

@app.post("/service")
async def manage_service(action: ServiceAction):
    """Manage local services"""
    cmd = f"sudo systemctl {action.action} {action.service}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return {
        "service": action.service,
        "action": action.action,
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout or result.stderr
    }

@app.post("/deploy")
async def deploy(request: DeploymentRequest):
    """Deploy application"""
    result = await executor.deploy_application({
        "branch": request.branch,
        "environment": request.environment
    })
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    metrics = await executor.monitor_infrastructure()
    return metrics

async def report_to_cloudflare(task_id: str, result: Dict):
    """Report task completion to Cloudflare Worker"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CLOUDFLARE_WORKER_URL}/api/task-complete",
                json={"task_id": task_id, "result": result}
            ) as response:
                logger.info(f"Reported to Cloudflare: {response.status}")
    except Exception as e:
        logger.error(f"Failed to report to Cloudflare: {e}")

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=LOCAL_API_PORT)
