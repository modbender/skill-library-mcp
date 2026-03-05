// ── System Monitor：CPU/MEM/Uptime 推送 ──

import os from 'os';
import { execFile } from 'child_process';
import { broadcastSystem, clientCount } from './sse.js';

let prevCpuTimes = null;

function getCpuUsage() {
  const cpus = os.cpus();
  let totalIdle = 0, totalTick = 0;
  for (const cpu of cpus) {
    const { user, nice, sys, idle, irq } = cpu.times;
    totalTick += user + nice + sys + idle + irq;
    totalIdle += idle;
  }
  if (!prevCpuTimes) { prevCpuTimes = { idle: totalIdle, total: totalTick }; return 0; }
  const idleDiff = totalIdle - prevCpuTimes.idle;
  const totalDiff = totalTick - prevCpuTimes.total;
  prevCpuTimes = { idle: totalIdle, total: totalTick };
  return totalDiff === 0 ? 0 : ((1 - idleDiff / totalDiff) * 100);
}

function getProcessCount() {
  return new Promise((resolve) => {
    execFile('ps', ['-e'], (err, stdout) => {
      if (err) { resolve(0); return; }
      resolve(stdout.trim().split('\n').length - 1);
    });
  });
}

function getMemoryUsage() {
  return new Promise((resolve) => {
    execFile('vm_stat', (err, stdout) => {
      const totalMem = os.totalmem();
      if (err) { resolve({ used: totalMem - os.freemem(), total: totalMem }); return; }
      const pageMatch = stdout.match(/page size of (\d+) bytes/);
      const page = pageMatch ? parseInt(pageMatch[1]) : 16384;
      const get = (key) => {
        const m = stdout.match(new RegExp(`${key}:\\s+(\\d+)`));
        return m ? parseInt(m[1]) * page : 0;
      };
      const used = get('Pages active') + get('Pages wired down') + get('Pages occupied by compressor');
      resolve({ used, total: totalMem });
    });
  });
}

export function startSystemMonitor() {
  getCpuUsage(); // baseline

  setInterval(async () => {
    if (clientCount() === 0) return;
    const cpu = getCpuUsage();
    const mem = await getMemoryUsage();
    const procs = await getProcessCount();
    broadcastSystem({
      cpu: Math.round(cpu * 10) / 10,
      mem: { used: Math.round(mem.used / 1073741824 * 10) / 10, total: Math.round(mem.total / 1073741824 * 10) / 10 },
      uptime: os.uptime(),
      procs,
    });
  }, 3000);
}
