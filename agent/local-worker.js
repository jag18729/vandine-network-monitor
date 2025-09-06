#!/usr/bin/env node
/**
 * Local Cloudflare Worker Simulator for ARM/Raspberry Pi
 * Runs the worker code locally since wrangler doesn't support ARM
 */

const http = require('http');
const url = require('url');

// Configuration
const PORT = 8787;
const AUTH_TOKEN = 'secret_auth_token_123';
const PI_EXECUTOR_URL = 'http://localhost:8000';

// In-memory storage (simulating KV)
const taskQueue = [];
const monitoringData = {
    lastCheck: Date.now(),
    alerts: [],
    metrics: {
        tasksProcessed: 0,
        avgResponseTime: 0,
        successRate: 100
    }
};

// Helper functions
function generateId() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

function isAuthenticated(req) {
    const auth = req.headers.authorization;
    return auth && auth === `Bearer ${AUTH_TOKEN}`;
}

// Request handler
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const method = req.method;

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Authentication check for protected routes
    if (pathname !== '/health' && !isAuthenticated(req)) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Unauthorized' }));
        return;
    }

    // Route handling
    try {
        if (pathname === '/status' && method === 'GET') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'operational',
                timestamp: new Date().toISOString(),
                queue: {
                    pending: taskQueue.filter(t => t.status === 'pending').length,
                    processing: taskQueue.filter(t => t.status === 'processing').length,
                    completed: taskQueue.filter(t => t.status === 'completed').length
                },
                metrics: monitoringData.metrics,
                executor: {
                    url: PI_EXECUTOR_URL,
                    status: 'connected'
                }
            }));
        }
        else if (pathname === '/health' && method === 'GET') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'healthy',
                worker: 'local-simulator',
                timestamp: new Date().toISOString()
            }));
        }
        else if (pathname === '/tasks' && method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', () => {
                const task = JSON.parse(body);
                const taskId = generateId();
                const newTask = {
                    id: taskId,
                    ...task,
                    status: 'pending',
                    createdAt: Date.now(),
                    updatedAt: Date.now()
                };
                taskQueue.push(newTask);
                monitoringData.metrics.tasksProcessed++;
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    taskId: taskId,
                    message: 'Task queued successfully'
                }));
            });
        }
        else if (pathname.startsWith('/tasks/') && method === 'GET') {
            const taskId = pathname.split('/')[2];
            const task = taskQueue.find(t => t.id === taskId);
            
            if (task) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(task));
            } else {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Task not found' }));
            }
        }
        else if (pathname === '/execute' && method === 'POST') {
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', async () => {
                const { taskId } = JSON.parse(body);
                const task = taskQueue.find(t => t.id === taskId);
                
                if (task) {
                    task.status = 'processing';
                    task.updatedAt = Date.now();
                    
                    // Simulate execution
                    setTimeout(() => {
                        task.status = 'completed';
                        task.result = { success: true, message: 'Task completed' };
                        task.updatedAt = Date.now();
                    }, 2000);
                    
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        success: true,
                        message: 'Task execution started'
                    }));
                } else {
                    res.writeHead(404, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Task not found' }));
                }
            });
        }
        else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Not found' }));
        }
    } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
    }
});

// Start server
server.listen(PORT, () => {
    console.log(`Local Worker Simulator running on http://localhost:${PORT}`);
    console.log('This simulates Cloudflare Worker functionality locally');
    console.log('Use this for development and testing on ARM/Raspberry Pi');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, closing server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});
