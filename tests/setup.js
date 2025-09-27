// Jest Setup File
process.env.NODE_ENV = 'test';

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
  log: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};

// Global test utilities
global.testUtils = {
  generateMockService: (name, status = 'online') => ({
    name,
    status,
    uptime: 99.97,
    lastCheck: new Date().toISOString(),
    responseTime: Math.random() * 100,
  }),
  
  generateMockCloudflareData: () => ({
    requests: Math.floor(Math.random() * 10000),
    bandwidth: Math.floor(Math.random() * 1000000),
    threats: Math.floor(Math.random() * 100),
    cached: Math.floor(Math.random() * 5000),
  }),
  
  generateMockPiholeData: () => ({
    queries_today: Math.floor(Math.random() * 50000),
    blocked_today: Math.floor(Math.random() * 10000),
    percent_blocked: (Math.random() * 30).toFixed(2),
    unique_clients: Math.floor(Math.random() * 50),
  }),
};

// Setup test timeouts
jest.setTimeout(10000);
EOFSETUP'
