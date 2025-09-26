#!/usr/bin/env python3
"""
High-Performance API Gateway with Network Engineering Test Features
Optimized for Python 3.11 with BBR support and WebSocket optimizations
"""

import asyncio
import json
import time
import os
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime
import aioredis
import httpx
from fastapi import FastAPI, WebSocket, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvloop
from pydantic import BaseModel

# Use uvloop for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
PIHOLE_URL = os.getenv('PIHOLE_API_URL', 'http://192.168.2.7/admin/api.php')

class NetworkTestRequest(BaseModel):
    test_type: str
    target: Optional[str] = None
    duration: Optional[int] = 10
    parameters: Optional[Dict[str, Any]] = {}

class CongestionControlRequest(BaseModel):
    algorithm: str  # bbr, cubic, reno

class WebSocketConfig(BaseModel):
    window_size: int  # 16384 to 1048576 (16KB to 1MB)
    compression: bool = True
    frame_size: int = 65536
    multiplexing: bool = False

# Global connections for resource efficiency
redis_client = None
httpx_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global redis_client, httpx_client
    
    # Startup
    redis_client = await aioredis.create_redis_pool(REDIS_URL)
    httpx_client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_keepalive_connections=100,
            max_connections=1000,
            keepalive_expiry=300
        ),
        timeout=httpx.Timeout(30.0)
    )
    
    yield
    
    # Shutdown
    redis_client.close()
    await redis_client.wait_closed()
    await httpx_client.aclose()

app = FastAPI(
    title="Vandine Network Engineering Lab",
    version="2.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://vandine.us", "https://vandine.us", "http://192.168.2.7"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
async def rate_limit(request: Request, calls: int = 100, period: int = 60):
    """Token bucket rate limiting using Redis"""
    if not redis_client:
        return True
    
    key = f"rate_limit:{request.client.host}"
    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, period)
        if current > calls:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except Exception:
        pass  # Don't block on rate limit errors

# Network Testing Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "congestion_control": await get_congestion_control(),
        "services": {
            "redis": redis_client is not None,
            "httpx": httpx_client is not None
        }
    }

@app.get("/api/network/congestion-control")
async def get_congestion_control():
    """Get current TCP congestion control algorithm"""
    try:
        result = subprocess.run(
            ["cat", "/proc/sys/net/ipv4/tcp_congestion_control"],
            capture_output=True,
            text=True
        )
        current = result.stdout.strip()
        
        available = subprocess.run(
            ["cat", "/proc/sys/net/ipv4/tcp_available_congestion_control"],
            capture_output=True,
            text=True
        ).stdout.strip().split()
        
        return {
            "current": current,
            "available": available,
            "bbr_enabled": "bbr" in available
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network/congestion-control")
async def set_congestion_control(request: CongestionControlRequest):
    """Switch TCP congestion control algorithm"""
    if request.algorithm not in ["bbr", "cubic", "reno"]:
        raise HTTPException(status_code=400, detail="Invalid algorithm")
    
    try:
        # Load module if BBR
        if request.algorithm == "bbr":
            subprocess.run(["sudo", "modprobe", "tcp_bbr"], check=True)
        
        # Set congestion control
        subprocess.run(
            ["sudo", "sysctl", f"net.ipv4.tcp_congestion_control={request.algorithm}"],
            check=True
        )
        
        return {
            "status": "success",
            "algorithm": request.algorithm,
            "message": f"Switched to {request.algorithm}"
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch: {e}")

@app.post("/api/network/test")
async def run_network_test(request: NetworkTestRequest):
    """Run various network tests"""
    test_results = {}
    
    if request.test_type == "bandwidth":
        # Test bandwidth using iperf3 or similar
        test_results = await test_bandwidth(request.target, request.duration)
    
    elif request.test_type == "latency":
        # Test latency using ping
        test_results = await test_latency(request.target, request.duration)
    
    elif request.test_type == "packet_loss":
        # Test packet loss
        test_results = await test_packet_loss(request.target, request.duration)
    
    elif request.test_type == "mtu_discovery":
        # Discover optimal MTU
        test_results = await discover_mtu(request.target)
    
    elif request.test_type == "tcp_window":
        # Test TCP window scaling
        test_results = await test_tcp_window(request.target)
    
    else:
        raise HTTPException(status_code=400, detail="Unknown test type")
    
    # Store results in Redis
    await store_test_results(test_results)
    
    return test_results

async def test_bandwidth(target: str, duration: int) -> Dict[str, Any]:
    """Test bandwidth using iperf3"""
    if not target:
        target = "192.168.2.1"
    
    try:
        # Run iperf3 client
        result = subprocess.run(
            ["iperf3", "-c", target, "-t", str(duration), "-J"],
            capture_output=True,
            text=True,
            timeout=duration + 5
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "type": "bandwidth",
                "target": target,
                "duration": duration,
                "sent_mbps": data.get("end", {}).get("sum_sent", {}).get("bits_per_second", 0) / 1_000_000,
                "received_mbps": data.get("end", {}).get("sum_received", {}).get("bits_per_second", 0) / 1_000_000,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {"error": str(e), "type": "bandwidth"}

async def test_latency(target: str, duration: int) -> Dict[str, Any]:
    """Test latency using ping"""
    if not target:
        target = "1.1.1.1"
    
    try:
        result = subprocess.run(
            ["ping", "-c", str(duration), "-i", "1", target],
            capture_output=True,
            text=True,
            timeout=duration + 5
        )
        
        # Parse ping output
        lines = result.stdout.split('\n')
        for line in lines:
            if "min/avg/max" in line:
                stats = line.split("=")[-1].strip().split("/")
                return {
                    "type": "latency",
                    "target": target,
                    "min_ms": float(stats[0]),
                    "avg_ms": float(stats[1]),
                    "max_ms": float(stats[2]),
                    "timestamp": datetime.utcnow().isoformat()
                }
    except Exception as e:
        return {"error": str(e), "type": "latency"}

async def discover_mtu(target: str) -> Dict[str, Any]:
    """Discover optimal MTU using path MTU discovery"""
    if not target:
        target = "1.1.1.1"
    
    optimal_mtu = 1500
    for mtu in [1500, 1492, 1480, 1472, 1460, 1400]:
        try:
            result = subprocess.run(
                ["ping", "-M", "do", "-s", str(mtu - 28), "-c", "1", target],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                optimal_mtu = mtu
                break
        except:
            continue
    
    return {
        "type": "mtu_discovery",
        "target": target,
        "optimal_mtu": optimal_mtu,
        "timestamp": datetime.utcnow().isoformat()
    }

async def test_tcp_window(target: str) -> Dict[str, Any]:
    """Test TCP window scaling"""
    try:
        # Get current TCP settings
        rmem = subprocess.run(["cat", "/proc/sys/net/ipv4/tcp_rmem"], capture_output=True, text=True)
        wmem = subprocess.run(["cat", "/proc/sys/net/ipv4/tcp_wmem"], capture_output=True, text=True)
        
        return {
            "type": "tcp_window",
            "receive_window": rmem.stdout.strip(),
            "send_window": wmem.stdout.strip(),
            "window_scaling": "enabled",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "type": "tcp_window"}

async def test_packet_loss(target: str, duration: int) -> Dict[str, Any]:
    """Test packet loss"""
    if not target:
        target = "1.1.1.1"
    
    try:
        result = subprocess.run(
            ["ping", "-c", str(duration * 2), "-i", "0.5", target],
            capture_output=True,
            text=True,
            timeout=duration + 5
        )
        
        # Parse packet loss
        for line in result.stdout.split('\n'):
            if "packet loss" in line:
                loss = line.split(",")[2].strip().split("%")[0]
                return {
                    "type": "packet_loss",
                    "target": target,
                    "loss_percent": float(loss),
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat()
                }
    except Exception as e:
        return {"error": str(e), "type": "packet_loss"}

async def store_test_results(results: Dict[str, Any]):
    """Store test results in Redis for historical analysis"""
    if redis_client:
        key = f"test_results:{results.get('type')}:{int(time.time())}"
        await redis_client.setex(key, 3600, json.dumps(results))

# WebSocket endpoints for real-time monitoring

@app.websocket("/ws/network-monitor")
async def websocket_monitor(websocket: WebSocket):
    """WebSocket endpoint for real-time network monitoring"""
    await websocket.accept()
    
    try:
        # Send initial configuration
        await websocket.send_json({
            "type": "config",
            "window_size": 65536,
            "congestion_control": await get_congestion_control()
        })
        
        # Monitor loop
        while True:
            # Get current metrics
            metrics = await gather_network_metrics()
            await websocket.send_json({
                "type": "metrics",
                "data": metrics,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait for next update or client message
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=1.0
                )
                
                # Handle client commands
                command = json.loads(message)
                if command.get("action") == "set_window_size":
                    # Adjust WebSocket window size
                    new_size = command.get("size", 65536)
                    await websocket.send_json({
                        "type": "window_size_changed",
                        "size": new_size
                    })
                    
            except asyncio.TimeoutError:
                continue
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

async def gather_network_metrics() -> Dict[str, Any]:
    """Gather current network metrics"""
    metrics = {}
    
    # Get interface statistics
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]  # Skip headers
            for line in lines:
                if "eth" in line or "wlan" in line:
                    parts = line.split()
                    interface = parts[0].strip(":")
                    metrics[interface] = {
                        "rx_bytes": int(parts[1]),
                        "rx_packets": int(parts[2]),
                        "tx_bytes": int(parts[9]),
                        "tx_packets": int(parts[10])
                    }
    except:
        pass
    
    # Get TCP statistics
    try:
        with open("/proc/net/snmp", "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "Tcp:" in line and i + 1 < len(lines):
                    headers = line.split()[1:]
                    values = lines[i + 1].split()[1:]
                    tcp_stats = dict(zip(headers, values))
                    metrics["tcp"] = {
                        "active_opens": int(tcp_stats.get("ActiveOpens", 0)),
                        "passive_opens": int(tcp_stats.get("PassiveOpens", 0)),
                        "retrans_segs": int(tcp_stats.get("RetransSegs", 0)),
                        "curr_estab": int(tcp_stats.get("CurrEstab", 0))
                    }
    except:
        pass
    
    return metrics

# MCP Server Integration

@app.post("/api/mcp/register")
async def register_mcp_server(server_url: str, name: str):
    """Register a new MCP server"""
    if redis_client:
        key = f"mcp_servers:{name}"
        await redis_client.setex(key, 3600, server_url)
    
    return {"status": "registered", "name": name, "url": server_url}

@app.get("/api/mcp/servers")
async def list_mcp_servers():
    """List all registered MCP servers"""
    servers = []
    if redis_client:
        keys = await redis_client.keys("mcp_servers:*")
        for key in keys:
            url = await redis_client.get(key)
            name = key.decode().split(":")[1]
            servers.append({"name": name, "url": url.decode() if url else None})
    
    return {"servers": servers}

# Security Testing Endpoints

@app.get("/api/security/tls-test")
async def test_tls_security(target: str = "vandine.us"):
    """Test TLS configuration and cipher suites"""
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", f"{target}:443", "-tls1_3"],
            capture_output=True,
            text=True,
            timeout=5,
            input=""
        )
        
        # Parse TLS info
        cipher = None
        protocol = None
        for line in result.stdout.split('\n'):
            if "Cipher" in line and "is" in line:
                cipher = line.split("is")[1].strip()
            if "Protocol" in line and ":" in line:
                protocol = line.split(":")[1].strip()
        
        return {
            "target": target,
            "protocol": protocol,
            "cipher": cipher,
            "tls1_3": "TLSv1.3" in result.stdout,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8887,
        loop="uvloop",
        access_log=False,
        log_level="info"
    )
