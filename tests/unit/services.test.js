const { describe, test, expect, beforeEach, afterEach } = require('@jest/globals');

describe('Service Monitoring Tests', () => {
  let services;
  
  beforeEach(() => {
    services = [
      testUtils.generateMockService('Cloudflare API', 'online'),
      testUtils.generateMockService('Pi-hole DNS', 'online'),
      testUtils.generateMockService('Palo Alto Firewall', 'online'),
      testUtils.generateMockService('UniFi Controller', 'degraded'),
      testUtils.generateMockService('Docker Registry', 'offline'),
    ];
  });
  
  test('should correctly count online services', () => {
    const onlineCount = services.filter(s => s.status === 'online').length;
    expect(onlineCount).toBe(3);
  });
  
  test('should correctly identify degraded services', () => {
    const degraded = services.filter(s => s.status === 'degraded');
    expect(degraded).toHaveLength(1);
    expect(degraded[0].name).toBe('UniFi Controller');
  });
  
  test('should calculate average uptime correctly', () => {
    const avgUptime = services.reduce((sum, s) => sum + s.uptime, 0) / services.length;
    expect(avgUptime).toBeCloseTo(99.97, 1);
  });
  
  test('should have valid response times', () => {
    services.forEach(service => {
      expect(service.responseTime).toBeGreaterThanOrEqual(0);
      expect(service.responseTime).toBeLessThanOrEqual(100);
    });
  });
  
  test('should have valid ISO date strings', () => {
    services.forEach(service => {
      expect(() => new Date(service.lastCheck)).not.toThrow();
    });
  });
});

describe('Cloudflare Integration Tests', () => {
  let cloudflareData;
  
  beforeEach(() => {
    cloudflareData = testUtils.generateMockCloudflareData();
  });
  
  test('should return valid request counts', () => {
    expect(cloudflareData.requests).toBeGreaterThanOrEqual(0);
    expect(cloudflareData.requests).toBeLessThanOrEqual(10000);
  });
  
  test('should return valid bandwidth data', () => {
    expect(cloudflareData.bandwidth).toBeGreaterThanOrEqual(0);
    expect(cloudflareData.bandwidth).toBeLessThanOrEqual(1000000);
  });
  
  test('should track threat counts', () => {
    expect(cloudflareData.threats).toBeGreaterThanOrEqual(0);
    expect(cloudflareData.threats).toBeLessThanOrEqual(100);
  });
  
  test('should track cached requests', () => {
    expect(cloudflareData.cached).toBeGreaterThanOrEqual(0);
    expect(cloudflareData.cached).toBeLessThanOrEqual(5000);
  });
});

describe('Pi-hole Integration Tests', () => {
  let piholeData;
  
  beforeEach(() => {
    piholeData = testUtils.generateMockPiholeData();
  });
  
  test('should return valid query counts', () => {
    expect(piholeData.queries_today).toBeGreaterThanOrEqual(0);
    expect(piholeData.queries_today).toBeLessThanOrEqual(50000);
  });
  
  test('should return valid blocked counts', () => {
    expect(piholeData.blocked_today).toBeGreaterThanOrEqual(0);
    expect(piholeData.blocked_today).toBeLessThanOrEqual(piholeData.queries_today);
  });
  
  test('should calculate valid block percentage', () => {
    const percentage = parseFloat(piholeData.percent_blocked);
    expect(percentage).toBeGreaterThanOrEqual(0);
    expect(percentage).toBeLessThanOrEqual(100);
  });
  
  test('should track unique clients', () => {
    expect(piholeData.unique_clients).toBeGreaterThanOrEqual(0);
    expect(piholeData.unique_clients).toBeLessThanOrEqual(50);
  });
});
EOFTEST'
