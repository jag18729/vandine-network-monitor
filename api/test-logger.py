#!/usr/bin/env python3
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class TestLogger:
    def __init__(self, db_path='/home/johnmarston/vandine-network-monitor/logs/api-tests/test_history.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for test history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    method TEXT DEFAULT 'GET',
                    request_body TEXT,
                    response_status INTEGER,
                    response_body TEXT,
                    response_time_ms REAL,
                    test_type TEXT,
                    test_name TEXT,
                    client_ip TEXT,
                    user_agent TEXT,
                    success BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON test_logs(timestamp DESC)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_test_type ON test_logs(test_type)
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_type TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    last_result TEXT,
                    last_run DATETIME,
                    run_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    avg_response_time_ms REAL,
                    UNIQUE(test_type, test_name)
                )
            ''')
    
    def generate_test_id(self, endpoint: str, method: str = 'GET', body: str = None) -> str:
        """Generate unique test ID based on request parameters"""
        content = f"{method}:{endpoint}:{body or ''}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def log_test(self, test_data: Dict) -> str:
        """Log a test execution"""
        test_id = self.generate_test_id(
            test_data.get('endpoint'),
            test_data.get('method', 'GET'),
            test_data.get('request_body')
        )
        
        with sqlite3.connect(self.db_path) as conn:
            # Log the test
            conn.execute('''
                INSERT OR REPLACE INTO test_logs 
                (test_id, endpoint, method, request_body, response_status, 
                 response_body, response_time_ms, test_type, test_name, 
                 client_ip, user_agent, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_id,
                test_data.get('endpoint'),
                test_data.get('method', 'GET'),
                json.dumps(test_data.get('request_body')) if test_data.get('request_body') else None,
                test_data.get('response_status'),
                json.dumps(test_data.get('response_body')),
                test_data.get('response_time_ms'),
                test_data.get('test_type'),
                test_data.get('test_name'),
                test_data.get('client_ip'),
                test_data.get('user_agent'),
                test_data.get('success', True)
            ))
            
            # Update test results summary
            conn.execute('''
                INSERT INTO test_results (test_type, test_name, last_result, last_run, run_count, success_count, avg_response_time_ms)
                VALUES (?, ?, ?, datetime('now'), 1, ?, ?)
                ON CONFLICT(test_type, test_name) DO UPDATE SET
                    last_result = excluded.last_result,
                    last_run = excluded.last_run,
                    run_count = run_count + 1,
                    success_count = success_count + CASE WHEN excluded.success_count > 0 THEN 1 ELSE 0 END,
                    avg_response_time_ms = (avg_response_time_ms * (run_count - 1) + ?) / run_count
            ''', (
                test_data.get('test_type', 'general'),
                test_data.get('test_name', test_data.get('endpoint')),
                json.dumps(test_data.get('response_body')),
                1 if test_data.get('success') else 0,
                test_data.get('response_time_ms', 0),
                test_data.get('response_time_ms', 0)
            ))
            
        return test_id
    
    def get_last_test(self, test_type: str = None, test_name: str = None) -> Optional[Dict]:
        """Get the last test result"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = 'SELECT * FROM test_logs WHERE 1=1'
            params = []
            
            if test_type:
                query += ' AND test_type = ?'
                params.append(test_type)
            
            if test_name:
                query += ' AND test_name = ?'
                params.append(test_name)
            
            query += ' ORDER BY timestamp DESC LIMIT 1'
            
            row = conn.execute(query, params).fetchone()
            
            if row:
                result = dict(row)
                if result.get('request_body'):
                    result['request_body'] = json.loads(result['request_body'])
                if result.get('response_body'):
                    result['response_body'] = json.loads(result['response_body'])
                return result
            
        return None
    
    def get_test_history(self, limit: int = 100, test_type: str = None) -> List[Dict]:
        """Get test history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = 'SELECT * FROM test_logs WHERE 1=1'
            params = []
            
            if test_type:
                query += ' AND test_type = ?'
                params.append(test_type)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                if result.get('request_body'):
                    try:
                        result['request_body'] = json.loads(result['request_body'])
                    except:
                        pass
                if result.get('response_body'):
                    try:
                        result['response_body'] = json.loads(result['response_body'])
                    except:
                        pass
                results.append(result)
            
            return results
    
    def get_test_stats(self) -> Dict:
        """Get test statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_tests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_tests,
                    AVG(response_time_ms) as avg_response_time,
                    MIN(response_time_ms) as min_response_time,
                    MAX(response_time_ms) as max_response_time,
                    COUNT(DISTINCT test_type) as test_types,
                    COUNT(DISTINCT endpoint) as unique_endpoints
                FROM test_logs
                WHERE timestamp > datetime('now', '-24 hours')
            ''').fetchone()
            
            return dict(stats) if stats else {}

# Export for use in other modules
logger = TestLogger()
