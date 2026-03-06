/**
 * Basic tests for ProtonMail skill
 * 
 * These are placeholder tests to validate the build system.
 * Full integration tests will be added as the skill develops.
 */

import ProtonMailSkill from '../src/index';

describe('ProtonMailSkill', () => {
  // Set test environment variables
  beforeAll(() => {
    process.env.PROTONMAIL_ACCOUNT = 'test@pm.me';
    process.env.PROTONMAIL_BRIDGE_PASSWORD = 'test-password';
  });
  
  afterAll(() => {
    delete process.env.PROTONMAIL_ACCOUNT;
    delete process.env.PROTONMAIL_BRIDGE_PASSWORD;
  });
  
  it('should instantiate with config object', () => {
    const skill = new ProtonMailSkill({
      account: 'test@pm.me',
      bridgePassword: 'test-password'
    });
    
    expect(skill).toBeDefined();
  });
  
  it('should instantiate from environment variables', () => {
    const skill = new ProtonMailSkill();
    
    expect(skill).toBeDefined();
  });
  
  it('should accept custom ports', () => {
    const skill = new ProtonMailSkill({
      account: 'test@pm.me',
      bridgePassword: 'test-password',
      imapPort: 9143,
      smtpPort: 9025
    });
    
    expect(skill).toBeDefined();
  });
});

describe('Configuration validation', () => {
  it('should throw error when account is missing', () => {
    delete process.env.PROTONMAIL_ACCOUNT;
    
    expect(() => {
      new ProtonMailSkill({ bridgePassword: 'test' });
    }).toThrow('ProtonMail account not configured');
    
    process.env.PROTONMAIL_ACCOUNT = 'test@pm.me';
  });
  
  it('should throw error when password is missing', () => {
    delete process.env.PROTONMAIL_BRIDGE_PASSWORD;
    
    expect(() => {
      new ProtonMailSkill({ account: 'test@pm.me' });
    }).toThrow('ProtonMail Bridge password not configured');
    
    process.env.PROTONMAIL_BRIDGE_PASSWORD = 'test-password';
  });
});
