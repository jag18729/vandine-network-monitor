// Cloudflare Worker for Vandine Network Monitor
// Handles WebSocket proxying and API routing with SSL

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const headers = new Headers(request.headers)
  
  // Handle WebSocket upgrade
  if (headers.get('Upgrade') === 'websocket') {
    return handleWebSocket(request)
  }
  
  // API routing
  if (url.pathname.startsWith('/api/')) {
    return handleAPI(request, url)
  }
  
  // Static content
  return fetch(request)
}

async function handleWebSocket(request) {
  const url = new URL(request.url)
  // Replace with your actual backend WebSocket
  const backendUrl = 'ws://192.168.2.7:8887' + url.pathname
  
  return fetch(backendUrl, request)
}

async function handleAPI(request, url) {
  const apiEndpoints = {
    '/api/network/status': 'http://192.168.2.7:8887/network/status',
    '/api/pihole/stats': 'http://192.168.2.7:8889/stats',
    '/api/dns/test': 'http://192.168.2.7:8887/dns/test',
    '/api/congestion/current': 'http://192.168.2.7:8887/congestion/current',
    '/api/congestion/switch': 'http://192.168.2.7:8887/congestion/switch'
  }
  
  const backendUrl = apiEndpoints[url.pathname] || 'http://192.168.2.7:8887' + url.pathname
  
  const modifiedRequest = new Request(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
  
  const response = await fetch(modifiedRequest)
  
  // Add CORS headers
  const modifiedResponse = new Response(response.body, response)
  modifiedResponse.headers.set('Access-Control-Allow-Origin', '*')
  modifiedResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  modifiedResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type')
  
  return modifiedResponse
}
