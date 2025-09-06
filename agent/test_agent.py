#!/usr/bin/env python3
"""
Test script for the Vandine Network Agent
"""
import requests
import json
import time
from datetime import datetime

# Configuration
WORKER_URL = "http://localhost:8787"  # Change to your deployed URL
PI_EXECUTOR_URL = "http://localhost:8000"
AUTH_TOKEN = "secret_auth_token_123"

def test_worker_api():
    """Test Cloudflare Worker endpoints"""
    print("Testing Cloudflare Worker API...")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Test status endpoint
    try:
        response = requests.get(f"{WORKER_URL}/status", headers=headers)
        if response.status_code == 200:
            print("✅ Status endpoint working")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to Worker: {e}")
    
    print()
    
    # Test task creation
    try:
        task_data = {
            "type": "dns_update",
            "priority": "high",
            "data": {
                "record": "test.vandine.us",
                "type": "A",
                "content": "192.168.1.100"
            }
        }
        response = requests.post(f"{WORKER_URL}/tasks", 
                                headers=headers,
                                json=task_data)
        if response.status_code == 200:
            print("✅ Task creation working")
            task_id = response.json().get("taskId")
            print(f"   Task ID: {task_id}")
        else:
            print(f"❌ Task creation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not create task: {e}")

def test_pi_executor():
    """Test Pi Executor endpoints"""
    print("\nTesting Pi Executor API...")
    print("="*50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{PI_EXECUTOR_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to Pi Executor: {e}")
    
    print()
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{PI_EXECUTOR_URL}/metrics")
        if response.status_code == 200:
            print("✅ Metrics endpoint working")
            metrics = response.json()
            print(f"   CPU: {metrics.get('cpu_percent', 'N/A')}%")
            print(f"   Memory: {metrics.get('memory_percent', 'N/A')}%")
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Could not get metrics: {e}")

def test_end_to_end():
    """Test full agent workflow"""
    print("\nTesting End-to-End Workflow...")
    print("="*50)
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Create a test task
    task_data = {
        "type": "system_check",
        "priority": "medium",
        "data": {
            "check_type": "network_connectivity",
            "targets": ["8.8.8.8", "1.1.1.1"]
        }
    }
    
    try:
        # Submit task to Worker
        response = requests.post(f"{WORKER_URL}/tasks", 
                                headers=headers,
                                json=task_data)
        if response.status_code == 200:
            task_id = response.json().get("taskId")
            print(f"✅ Task submitted: {task_id}")
            
            # Wait for execution
            print("   Waiting for execution...")
            time.sleep(2)
            
            # Check task status
            response = requests.get(f"{WORKER_URL}/tasks/{task_id}", 
                                   headers=headers)
            if response.status_code == 200:
                status = response.json().get("status")
                print(f"✅ Task status: {status}")
            else:
                print(f"❌ Could not get task status")
        else:
            print(f"❌ Task submission failed")
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")

def main():
    print("\n" + "="*60)
    print(" Vandine Network Agent Test Suite")
    print("="*60)
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run tests
    test_pi_executor()
    test_worker_api()
    test_end_to_end()
    
    print("\n" + "="*60)
    print(" Test Suite Complete")
    print("="*60)

if __name__ == "__main__":
    main()
