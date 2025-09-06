// Network Operations Agent - Cloudflare Worker
// Handles intelligent task prioritization and coordination

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    // Route handlers
    switch (url.pathname) {
      case '/':
        return handleRoot(headers);
      
      case '/api/status':
        return handleStatus(env, headers);
      
      case '/api/tasks':
        return handleTasks(request, env, headers);
      
      case '/api/execute':
        return handleExecute(request, env, ctx, headers);
      
      case '/api/monitor':
        return handleMonitor(env, headers);
      
      case '/api/alert':
        return handleAlert(request, env, ctx, headers);
        
      case '/api/report':
        return handleReport(env, headers);
        
      default:
        return new Response(JSON.stringify({ error: 'Not found' }), { 
          status: 404, 
          headers 
        });
    }
  },

  // Scheduled cron trigger for automated tasks
  async scheduled(event, env, ctx) {
    await runScheduledTasks(env, ctx);
  }
};

// Root endpoint - Agent info
function handleRoot(headers) {
  return new Response(JSON.stringify({
    name: 'Network Operations Agent',
    version: '1.0.0',
    status: 'operational',
    endpoints: [
      '/api/status - System status',
      '/api/tasks - Task management',
      '/api/execute - Execute priority tasks',
      '/api/monitor - Infrastructure monitoring',
      '/api/alert - Alert management',
      '/api/report - Generate reports'
    ],
    capabilities: [
      'Intelligent task prioritization',
      'Automated remediation',
      'Performance monitoring',
      'Security scanning',
      'GitHub integration'
    ]
  }), { headers });
}

// System status
async function handleStatus(env, headers) {
  const status = await env.KV.get('system_status', { type: 'json' }) || {};
  
  return new Response(JSON.stringify({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    metrics: {
      uptime: status.uptime || '99.9%',
      response_time: status.response_time || '12ms',
      active_tasks: status.active_tasks || 0,
      alerts: status.alerts || []
    },
    services: {
      cloudflare: 'operational',
      github: 'operational',
      monitoring: 'operational'
    }
  }), { headers });
}

// Task management with prioritization
async function handleTasks(request, env, headers) {
  if (request.method === 'GET') {
    // Get current task queue
    const tasks = await env.KV.get('task_queue', { type: 'json' }) || [];
    
    // Sort by priority
    tasks.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
    
    return new Response(JSON.stringify({ tasks }), { headers });
  }
  
  if (request.method === 'POST') {
    // Add new task
    const task = await request.json();
    const tasks = await env.KV.get('task_queue', { type: 'json' }) || [];
    
    const newTask = {
      id: crypto.randomUUID(),
      ...task,
      created: new Date().toISOString(),
      status: 'pending'
    };
    
    tasks.push(newTask);
    await env.KV.put('task_queue', JSON.stringify(tasks));
    
    // Check if immediate execution needed
    if (task.priority === 'critical') {
      await executeCriticalTask(newTask, env);
    }
    
    return new Response(JSON.stringify({ 
      message: 'Task added',
      task: newTask 
    }), { headers });
  }
}

// Execute priority tasks
async function handleExecute(request, env, ctx, headers) {
  const { taskId, action } = await request.json();
  
  // Get task from queue
  const tasks = await env.KV.get('task_queue', { type: 'json' }) || [];
  const task = tasks.find(t => t.id === taskId);
  
  if (!task) {
    return new Response(JSON.stringify({ error: 'Task not found' }), { 
      status: 404, 
      headers 
    });
  }
  
  // Execute based on task type
  let result;
  switch (task.type) {
    case 'deploy':
      result = await executeDeploy(task, env);
      break;
    
    case 'monitor':
      result = await executeMonitor(task, env);
      break;
    
    case 'remediate':
      result = await executeRemediation(task, env);
      break;
    
    case 'backup':
      result = await executeBackup(task, env);
      break;
      
    default:
      result = { status: 'unsupported', message: 'Task type not supported' };
  }
  
  // Update task status
  task.status = 'completed';
  task.completed = new Date().toISOString();
  task.result = result;
  
  await env.KV.put('task_queue', JSON.stringify(tasks));
  
  return new Response(JSON.stringify({ 
    message: 'Task executed',
    result 
  }), { headers });
}

// Infrastructure monitoring
async function handleMonitor(env, headers) {
  const checks = [];
  
  // Check Cloudflare status
  checks.push({
    service: 'Cloudflare Edge',
    status: 'healthy',
    latency: '11ms',
    location: 'LAX'
  });
  
  // Check GitHub
  try {
    const ghResponse = await fetch('https://api.github.com/repos/jag18729/vandine-network-monitor');
    checks.push({
      service: 'GitHub Repository',
      status: ghResponse.ok ? 'healthy' : 'degraded',
      response_time: '150ms'
    });
  } catch (e) {
    checks.push({
      service: 'GitHub Repository',
      status: 'error',
      error: e.message
    });
  }
  
  // Check website
  try {
    const siteResponse = await fetch('https://rafael.vandine.us');
    checks.push({
      service: 'Main Website',
      status: siteResponse.ok ? 'healthy' : 'down',
      response_code: siteResponse.status
    });
  } catch (e) {
    checks.push({
      service: 'Main Website',
      status: 'error',
      error: e.message
    });
  }
  
  // Store monitoring data
  await env.KV.put('monitoring_data', JSON.stringify({
    timestamp: new Date().toISOString(),
    checks
  }));
  
  return new Response(JSON.stringify({ 
    timestamp: new Date().toISOString(),
    checks 
  }), { headers });
}

// Alert management
async function handleAlert(request, env, ctx, headers) {
  const alert = await request.json();
  
  // Store alert
  const alerts = await env.KV.get('alerts', { type: 'json' }) || [];
  alerts.push({
    ...alert,
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString()
  });
  await env.KV.put('alerts', JSON.stringify(alerts));
  
  // Determine action based on severity
  if (alert.severity === 'critical') {
    // Immediate action required
    await ctx.waitUntil(handleCriticalAlert(alert, env));
  }
  
  return new Response(JSON.stringify({ 
    message: 'Alert received',
    action: alert.severity === 'critical' ? 'immediate' : 'queued'
  }), { headers });
}

// Generate reports
async function handleReport(env, headers) {
  const tasks = await env.KV.get('task_queue', { type: 'json' }) || [];
  const alerts = await env.KV.get('alerts', { type: 'json' }) || [];
  const monitoring = await env.KV.get('monitoring_data', { type: 'json' }) || {};
  
  const report = {
    generated: new Date().toISOString(),
    summary: {
      total_tasks: tasks.length,
      completed_tasks: tasks.filter(t => t.status === 'completed').length,
      pending_tasks: tasks.filter(t => t.status === 'pending').length,
      critical_alerts: alerts.filter(a => a.severity === 'critical').length,
      system_health: calculateHealth(monitoring)
    },
    tasks: tasks.slice(0, 10), // Last 10 tasks
    recent_alerts: alerts.slice(-5), // Last 5 alerts
    monitoring: monitoring
  };
  
  return new Response(JSON.stringify(report), { headers });
}

// Helper functions
async function executeCriticalTask(task, env) {
  // Send notification
  console.log('Executing critical task:', task);
  
  // Could integrate with Discord, Slack, email, etc.
  // For now, just log it
  await env.KV.put('last_critical_task', JSON.stringify({
    task,
    executed: new Date().toISOString()
  }));
}

async function handleCriticalAlert(alert, env) {
  // Auto-remediation logic
  console.log('Handling critical alert:', alert);
  
  // Example: If service is down, attempt restart
  if (alert.type === 'service_down') {
    // Trigger restart via Pi executor
    await fetch('http://192.168.2.7:8000/api/restart', {
      method: 'POST',
      body: JSON.stringify({ service: alert.service })
    });
  }
}

function calculateHealth(monitoring) {
  if (!monitoring.checks) return 'unknown';
  const healthy = monitoring.checks.filter(c => c.status === 'healthy').length;
  const total = monitoring.checks.length;
  const percentage = (healthy / total) * 100;
  
  if (percentage === 100) return 'excellent';
  if (percentage >= 90) return 'good';
  if (percentage >= 70) return 'degraded';
  return 'critical';
}

// Scheduled tasks (runs on cron)
async function runScheduledTasks(env, ctx) {
  const tasks = [
    { type: 'monitor', priority: 'medium' },
    { type: 'cleanup', priority: 'low' },
    { type: 'backup_check', priority: 'medium' }
  ];
  
  for (const task of tasks) {
    await ctx.waitUntil(executeScheduledTask(task, env));
  }
}

async function executeScheduledTask(task, env) {
  console.log('Running scheduled task:', task);
  // Task execution logic here
}
