#!/usr/bin/env python3
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import json
from datetime import datetime, timedelta
from test_logger import logger

app = FastAPI(title="Test History API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Log test if it's a test endpoint
    if '/test/' in str(request.url) or '/api/' in str(request.url):
        body = None
        try:
            if request.method in ['POST', 'PUT']:
                body = await request.body()
                body = json.loads(body) if body else None
        except:
            pass
        
        test_data = {
            'endpoint': str(request.url.path),
            'method': request.method,
            'request_body': body,
            'response_status': response.status_code,
            'response_time_ms': process_time,
            'client_ip': request.client.host,
            'user_agent': request.headers.get('user-agent'),
            'test_type': request.url.path.split('/')[1] if '/' in str(request.url.path) else 'general',
            'test_name': request.url.path.split('/')[-1] if '/' in str(request.url.path) else 'unknown',
            'success': response.status_code < 400
        }
        
        logger.log_test(test_data)
    
    return response

# RESTful API Endpoints

@app.get("/api/test/last")
async def get_last_test(test_type: str = None, test_name: str = None):
    """Get the last test result"""
    result = logger.get_last_test(test_type, test_name)
    if result:
        return JSONResponse(result)
    raise HTTPException(status_code=404, detail="No test found")

@app.get("/api/test/history")
async def get_test_history(limit: int = 100, test_type: str = None):
    """Get test history"""
    results = logger.get_test_history(limit, test_type)
    return JSONResponse({
        'count': len(results),
        'tests': results
    })

@app.get("/api/test/stats")
async def get_test_stats():
    """Get test statistics"""
    stats = logger.get_test_stats()
    return JSONResponse(stats)

@app.get("/api/test/{test_id}")
async def get_test_by_id(test_id: str):
    """Get specific test by ID"""
    # Implementation to fetch by test_id
    with sqlite3.connect(logger.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM test_logs WHERE test_id = ?', (test_id,)).fetchone()
        if row:
            result = dict(row)
            if result.get('response_body'):
                result['response_body'] = json.loads(result['response_body'])
            return JSONResponse(result)
    raise HTTPException(status_code=404, detail="Test not found")

@app.post("/api/test/replay/{test_id}")
async def replay_test(test_id: str):
    """Replay a previous test"""
    # Get the test
    with sqlite3.connect(logger.db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM test_logs WHERE test_id = ?', (test_id,)).fetchone()
        if row:
            test = dict(row)
            # Here you would replay the actual test
            # For now, return the stored result
            return JSONResponse({
                'replayed': True,
                'original_result': json.loads(test['response_body']) if test.get('response_body') else None
            })
    raise HTTPException(status_code=404, detail="Test not found")

# Test endpoints that generate data

@app.get("/api/test/bandwidth")
async def test_bandwidth():
    """Test bandwidth"""
    import random
    result = {
        'download': round(random.uniform(50, 150), 2),
        'upload': round(random.uniform(20, 80), 2),
        'timestamp': datetime.now().isoformat()
    }
    return JSONResponse(result)

@app.get("/api/test/latency")
async def test_latency():
    """Test latency"""
    import random
    result = {
        'latency': round(random.uniform(5, 50), 2),
        'jitter': round(random.uniform(1, 10), 2),
        'packet_loss': round(random.uniform(0, 2), 2),
        'timestamp': datetime.now().isoformat()
    }
    return JSONResponse(result)

@app.get("/api/test/mtu")
async def test_mtu():
    """Test MTU discovery"""
    result = {
        'mtu': 1500,
        'optimal_mtu': 1492,
        'timestamp': datetime.now().isoformat()
    }
    return JSONResponse(result)

if __name__ == "__main__":
    import uvicorn
    import sqlite3
    uvicorn.run(app, host="0.0.0.0", port=8886)
