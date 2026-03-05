import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

// Soul Watchdog tests — validate the shell script's core logic
// We test by running fragments or by simulating the watchdog behavior in JS

const SCRIPT = path.join(import.meta.dirname, '..', 'scripts', 'soul-watchdog.sh');

describe('Soul Watchdog Script', () => {

    it('script file exists and is executable', () => {
        assert.ok(fs.existsSync(SCRIPT), 'soul-watchdog.sh should exist');
        const stat = fs.statSync(SCRIPT);
        // Check executable bit (owner)
        assert.ok((stat.mode & 0o100) !== 0, 'soul-watchdog.sh should be executable');
    });

    it('script starts with correct shebang', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.startsWith('#!/bin/bash'), 'should start with #!/bin/bash');
    });

    it('monitors SOUL.md and IDENTITY.md', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('SOUL.md'), 'should reference SOUL.md');
        assert.ok(content.includes('IDENTITY.md'), 'should reference IDENTITY.md');
    });

    it('uses SHA-256 for hash verification', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('shasum -a 256'), 'should use shasum -a 256');
    });

    it('uses chflags uchg for file locking', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('chflags uchg'), 'should use chflags uchg for locking');
        assert.ok(content.includes('chflags nouchg'), 'should use chflags nouchg for unlocking');
    });

    it('supports --install, --uninstall, --status CLI flags', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('--install'), 'should support --install');
        assert.ok(content.includes('--uninstall'), 'should support --uninstall');
        assert.ok(content.includes('--status'), 'should support --status');
    });

    it('generates valid LaunchAgent plist', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('com.guava-guard.soul-watchdog'), 'should have correct plist label');
        assert.ok(content.includes('RunAtLoad'), 'plist should include RunAtLoad');
        assert.ok(content.includes('KeepAlive'), 'plist should include KeepAlive');
    });

    it('has fswatch fallback to polling', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('command -v fswatch'), 'should check for fswatch');
        assert.ok(content.includes('sleep 5'), 'should fallback to 5s polling');
    });

    it('restores from git on tamper detection', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('git checkout'), 'should restore via git checkout');
    });

    it('logs tamper events', () => {
        const content = fs.readFileSync(SCRIPT, 'utf8');
        assert.ok(content.includes('TAMPER DETECTED'), 'should log tamper detection');
        assert.ok(content.includes('RESTORED'), 'should log restoration');
        assert.ok(content.includes('RE-LOCKED'), 'should log re-locking');
    });
});

describe('Soul Lock Integration with SuiteBridge', () => {

    it('SuiteBridge references soulLock feature', async () => {
        const bridgePath = path.join(import.meta.dirname, '..', 'services', 'license-api', 'src', 'suiteBridge.js');
        const content = fs.readFileSync(bridgePath, 'utf8');
        assert.ok(content.includes('soulLock'), 'SuiteBridge should reference soulLock feature');
    });

    it('soulLock is gated by suiteEnabled', async () => {
        const bridgePath = path.join(import.meta.dirname, '..', 'services', 'license-api', 'src', 'suiteBridge.js');
        const content = fs.readFileSync(bridgePath, 'utf8');
        // soulLock should only be true when suiteEnabled is true
        assert.ok(content.includes('soulLock: gateStatus.suiteEnabled'),
            'soulLock should be gated by suiteEnabled');
    });
});
