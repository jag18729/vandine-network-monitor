/**
 * Unified API Gateway for Vandine Network Monitor
 * Routes requests to appropriate microservices
 */

const express = require('express');
const httpProxy = require('http-proxy-middleware');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const morgan = require('morgan');
const jwt = require('jsonwebtoken');
const WebSocket = require('ws');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Configuration
const PORT = process.env.API_GATEWAY_PORT || 8888;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Service endpoints
const services = {
  pihole: process.env.PIHOLE_SERVICE_URL || 'http://localhost:8889',
  cloudflare: process.env.CLOUDFLARE_SERVICE_URL || 'http://localhost:8787',
  metrics: process.env.METRICS_SERVICE_URL || 'http://localhost:8000',
  agent: process.env.AGENT_SERVICE_URL || 'http://localhost:8001'
};

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || '*',
  credentials: true
}));
app.use(express.json());
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// Authentication middleware (optional - can be enabled per route)
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token && process.env.REQUIRE_AUTH === 'true') {
    return res.sendStatus(401);
  }
  
  if (token) {
    jwt.verify(token, JWT_SECRET, (err, user) => {
      if (err) return res.sendStatus(403);
      req.user = user;
    });
  }
  
  next();
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: Object.keys(services),
    uptime: process.uptime()
  });
});

// Service status endpoint
app.get('/api/status', async (req, res) => {
  const statuses = {};
  
  for (const [name, url] of Object.entries(services)) {
    try {
      const response = await fetch(`${url}/health`);
      statuses[name] = response.ok ? 'online' : 'offline';
    } catch (error) {
      statuses[name] = 'offline';
    }
  }
  
  res.json({
    gateway: 'online',
    services: statuses,
    timestamp: new Date().toISOString()
  });
});

// Proxy configuration
const createProxyMiddleware = (target) => {
  return httpProxy.createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite: {
      '^/api/[^/]+': '' // Remove service prefix from path
    },
    onError: (err, req, res) => {
      console.error(`Proxy error: ${err.message}`);
      res.status(500).json({
        error: 'Service unavailable',
        message: err.message
      });
    },
    onProxyReq: (proxyReq, req, res) => {
      // Add custom headers if needed
      if (req.user) {
        proxyReq.setHeader('X-User-Id', req.user.id);
      }
    }
  });
};

// Route to Pi-hole service
app.use('/api/pihole', authenticateToken, createProxyMiddleware(services.pihole));

// Route to Cloudflare service
app.use('/api/cloudflare', authenticateToken, createProxyMiddleware(services.cloudflare));

// Route to Metrics service
app.use('/api/metrics', authenticateToken, createProxyMiddleware(services.metrics));

// Route to Agent service
app.use('/api/agent', authenticateToken, createProxyMiddleware(services.agent));

// WebSocket handling for real-time updates
const clients = new Set();

wss.on('connection', (ws, req) => {
  console.log('New WebSocket connection');
  clients.add(ws);
  
  // Send initial connection message
  ws.send(JSON.stringify({
    type: 'connected',
    timestamp: new Date().toISOString()
  }));
  
  // Handle incoming messages
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      // Handle different message types
      switch (data.type) {
        case 'subscribe':
          // Subscribe to specific data streams
          ws.subscriptions = data.channels || [];
          break;
          
        case 'ping':
          // Respond to ping
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
          
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('WebSocket message error:', error);
    }
  });
  
  // Handle disconnection
  ws.on('close', () => {
    console.log('WebSocket connection closed');
    clients.delete(ws);
  });
  
  // Handle errors
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    clients.delete(ws);
  });
});

// Broadcast function for real-time updates
const broadcast = (data, channel = null) => {
  const message = JSON.stringify({
    ...data,
    timestamp: new Date().toISOString()
  });
  
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      // If channel specified, only send to subscribed clients
      if (!channel || (client.subscriptions && client.subscriptions.includes(channel))) {
        client.send(message);
      }
    }
  });
};

// Poll Pi-hole for real-time updates (every 5 seconds)
setInterval(async () => {
  try {
    const response = await fetch(`${services.pihole}/api/pihole/summary`);
    if (response.ok) {
      const data = await response.json();
      broadcast({
        type: 'pihole-update',
        data: data
      }, 'pihole');
    }
  } catch (error) {
    console.error('Failed to fetch Pi-hole data:', error);
  }
}, 5000);

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log('Services configured:');
  Object.entries(services).forEach(([name, url]) => {
    console.log(`  - ${name}: ${url}`);
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

module.exports = { app, broadcast };
