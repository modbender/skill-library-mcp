/**
 * VirtualBox Utility Functions
 * 
 * Helper functions for managing VirtualBox VMs programmatically.
 * Requires VBoxManage CLI to be installed and accessible.
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Default VBoxManage command (can be overridden for different platforms)
const VBOXMANAGE = process.env.VBOXMANAGE_PATH || 'VBoxManage';

/**
 * Execute a VBoxManage command
 */
async function vboxCommand(args: string): Promise<{ stdout: string; stderr: string }> {
  try {
    const { stdout, stderr } = await execAsync(`${VBOXMANAGE} ${args}`);
    return { stdout, stderr };
  } catch (error: any) {
    throw new Error(`VBoxManage command failed: ${error.message}`);
  }
}

// ============================================
// VM Listing and Information
// ============================================

interface VMInfo {
  name: string;
  uuid: string;
  state: string;
}

/**
 * List all registered VMs
 */
export async function listVMs(): Promise<VMInfo[]> {
  const { stdout } = await vboxCommand('list vms');
  const vms: VMInfo[] = [];
  
  const lines = stdout.trim().split('\n');
  for (const line of lines) {
    if (!line) continue;
    const match = line.match(/^"(.+)"\s+\{(.+)\}$/);
    if (match) {
      vms.push({
        name: match[1],
        uuid: match[2],
        state: 'unknown'
      });
    }
  }
  
  return vms;
}

/**
 * List all running VMs
 */
export async function listRunningVMs(): Promise<VMInfo[]> {
  const { stdout } = await vboxCommand('list runningvms');
  const vms: VMInfo[] = [];
  
  const lines = stdout.trim().split('\n');
  for (const line of lines) {
    if (!line) continue;
    const match = line.match(/^"(.+)"\s+\{(.+)\}$/);
    if (match) {
      vms.push({
        name: match[1],
        uuid: match[2],
        state: 'running'
      });
    }
  }
  
  return vms;
}

/**
 * Get detailed information about a VM
 */
export async function getVMInfo(vmName: string): Promise<Record<string, string>> {
  const { stdout } = await vboxCommand(`showvminfo "${vmName}" --machinereadable`);
  const info: Record<string, string> = {};
  
  const lines = stdout.trim().split('\n');
  for (const line of lines) {
    const match = line.match(/^(.+)="(.*)"$/);
    if (match) {
      info[match[1]] = match[2];
    }
  }
  
  return info;
}

/**
 * Check if a VM exists
 */
export async function vmExists(vmName: string): Promise<boolean> {
  try {
    const vms = await listVMs();
    return vms.some(vm => vm.name === vmName || vm.uuid === vmName);
  } catch {
    return false;
  }
}

/**
 * Check if a VM is running
 */
export async function isVMRunning(vmName: string): Promise<boolean> {
  const running = await listRunningVMs();
  return running.some(vm => vm.name === vmName || vm.uuid === vmName);
}

// ============================================
// VM Lifecycle Management
// ============================================

/**
 * Start a VM
 */
export async function startVM(vmName: string, headless: boolean = true): Promise<void> {
  const type = headless ? '--type headless' : '';
  await vboxCommand(`startvm "${vmName}" ${type}`);
}

/**
 * Stop a VM gracefully (ACPI shutdown)
 */
export async function stopVM(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" acpipowerbutton`);
}

/**
 * Force stop a VM (power off)
 */
export async function forceStopVM(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" poweroff`);
}

/**
 * Pause a running VM
 */
export async function pauseVM(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" pause`);
}

/**
 * Resume a paused VM
 */
export async function resumeVM(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" resume`);
}

/**
 * Reset a VM (hard reboot)
 */
export async function resetVM(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" reset`);
}

/**
 * Save VM state (hibernate)
 */
export async function saveVMState(vmName: string): Promise<void> {
  await vboxCommand(`controlvm "${vmName}" savestate`);
}

// ============================================
// VM Creation and Deletion
// ============================================

interface VMCreateOptions {
  name: string;
  osType?: string;
  memory?: number;
  cpus?: number;
  diskSize?: number;
  diskPath?: string;
}

/**
 * Create a new VM
 */
export async function createVM(options: VMCreateOptions): Promise<string> {
  const { name, osType = 'Other_64', memory = 2048, cpus = 1, diskSize, diskPath } = options;
  
  // Create and register VM
  await vboxCommand(`createvm --name "${name}" --ostype "${osType}" --register`);
  
  // Set memory and CPU
  await vboxCommand(`modifyvm "${name}" --memory ${memory} --cpus ${cpus}`);
  
  // Create disk if size specified
  if (diskSize && diskPath) {
    await vboxCommand(`createhd --filename "${diskPath}" --size ${diskSize}`);
    await vboxCommand(`storagectl "${name}" --name "SATA Controller" --add sata`);
    await vboxCommand(`storageattach "${name}" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "${diskPath}"`);
  }
  
  return name;
}

/**
 * Delete a VM
 */
export async function deleteVM(vmName: string, deleteFiles: boolean = false): Promise<void> {
  const flag = deleteFiles ? '--delete' : '';
  await vboxCommand(`unregistervm "${vmName}" ${flag}`);
}

/**
 * Clone a VM
 */
export async function cloneVM(sourceName: string, targetName: string, linked: boolean = false): Promise<void> {
  const options = linked ? '--options link' : '';
  await vboxCommand(`clonevm "${sourceName}" --name "${targetName}" ${options} --register`);
}

// ============================================
// Snapshot Management
// ============================================

interface SnapshotInfo {
  name: string;
  uuid: string;
  description?: string;
  timestamp?: string;
}

/**
 * List snapshots for a VM
 */
export async function listSnapshots(vmName: string): Promise<SnapshotInfo[]> {
  try {
    const { stdout } = await vboxCommand(`snapshot "${vmName}" list --machinereadable`);
    const snapshots: SnapshotInfo[] = [];
    
    // Parse machine-readable snapshot output
    const lines = stdout.trim().split('\n');
    const currentSnapshot: Partial<SnapshotInfo> = {};
    
    for (const line of lines) {
      // Parse SnapshotName="..."
      // Parse SnapshotUUID="..."
      const nameMatch = line.match(/SnapshotName="(.+)"/);
      const uuidMatch = line.match(/SnapshotUUID="(.+)"/);
      
      if (nameMatch) {
        currentSnapshot.name = nameMatch[1];
      }
      if (uuidMatch) {
        currentSnapshot.uuid = uuidMatch[1];
        if (currentSnapshot.name) {
          snapshots.push(currentSnapshot as SnapshotInfo);
        }
      }
    }
    
    return snapshots;
  } catch {
    return [];
  }
}

/**
 * Take a snapshot
 */
export async function takeSnapshot(vmName: string, snapshotName: string, description?: string): Promise<void> {
  const desc = description ? `--description "${description}"` : '';
  await vboxCommand(`snapshot "${vmName}" take "${snapshotName}" ${desc}`);
}

/**
 * Restore a snapshot
 */
export async function restoreSnapshot(vmName: string, snapshotName: string): Promise<void> {
  await vboxCommand(`snapshot "${vmName}" restore "${snapshotName}"`);
}

/**
 * Delete a snapshot
 */
export async function deleteSnapshot(vmName: string, snapshotName: string): Promise<void> {
  await vboxCommand(`snapshot "${vmName}" delete "${snapshotName}"`);
}

// ============================================
// Network Configuration
// ============================================

type NetworkMode = 'none' | 'nat' | 'bridged' | 'hostonly' | 'internal';

/**
 * Configure network adapter
 */
export async function configureNetwork(
  vmName: string,
  adapter: number,
  mode: NetworkMode,
  options?: { bridgeAdapter?: string; hostOnlyAdapter?: string }
): Promise<void> {
  let cmd = `modifyvm "${vmName}" --nic${adapter} ${mode}`;
  
  if (mode === 'bridged' && options?.bridgeAdapter) {
    cmd += ` --bridgeadapter${adapter} "${options.bridgeAdapter}"`;
  }
  
  if (mode === 'hostonly' && options?.hostOnlyAdapter) {
    cmd += ` --hostonlyadapter${adapter} "${options.hostOnlyAdapter}"`;
  }
  
  await vboxCommand(cmd);
}

/**
 * Add NAT port forwarding rule
 */
export async function addPortForward(
  vmName: string,
  ruleName: string,
  hostPort: number,
  guestPort: number,
  protocol: 'tcp' | 'udp' = 'tcp',
  adapter: number = 1
): Promise<void> {
  await vboxCommand(
    `modifyvm "${vmName}" --natpf${adapter} "${ruleName},${protocol},,${hostPort},,${guestPort}"`
  );
}

/**
 * Remove NAT port forwarding rule
 */
export async function removePortForward(vmName: string, ruleName: string, adapter: number = 1): Promise<void> {
  await vboxCommand(`modifyvm "${vmName}" --natpf${adapter} delete "${ruleName}"`);
}

/**
 * List host-only interfaces
 */
export async function listHostOnlyInterfaces(): Promise<string[]> {
  const { stdout } = await vboxCommand('list hostonlyifs');
  const interfaces: string[] = [];
  
  const lines = stdout.split('\n');
  for (const line of lines) {
    const match = line.match(/^Name:\s+(.+)$/);
    if (match) {
      interfaces.push(match[1]);
    }
  }
  
  return interfaces;
}

// ============================================
// Resource Configuration
// ============================================

/**
 * Set VM memory
 */
export async function setMemory(vmName: string, memoryMB: number): Promise<void> {
  await vboxCommand(`modifyvm "${vmName}" --memory ${memoryMB}`);
}

/**
 * Set VM CPU count
 */
export async function setCPUs(vmName: string, cpus: number): Promise<void> {
  await vboxCommand(`modifyvm "${vmName}" --cpus ${cpus}`);
}

/**
 * Configure VM for performance
 */
export async function configurePerformance(
  vmName: string,
  options: {
    nestedVirtualization?: boolean;
    hardwareVirtualization?: boolean;
    largePages?: boolean;
  }
): Promise<void> {
  const { nestedVirtualization = false, hardwareVirtualization = true, largePages = true } = options;
  
  const commands = [
    `--hwvirtex ${hardwareVirtualization ? 'on' : 'off'}`,
    `--nested-hw-virt ${nestedVirtualization ? 'on' : 'off'}`,
    `--largepages ${largePages ? 'on' : 'off'}`
  ];
  
  await vboxCommand(`modifyvm "${vmName}" ${commands.join(' ')}`);
}

// ============================================
// Metrics and Monitoring
// ============================================

interface VMMetrics {
  cpuLoad?: string;
  ramUsage?: string;
  netRate?: string;
}

/**
 * Setup metrics collection
 */
export async function setupMetrics(vmName: string, period: number = 10, samples: number = 5): Promise<void> {
  await vboxCommand(`metrics setup --period ${period} --samples ${samples} "${vmName}"`);
}

/**
 * Query VM metrics
 */
export async function queryMetrics(vmName: string): Promise<VMMetrics> {
  const { stdout } = await vboxCommand(`metrics query "${vmName}" "CPU/Load:RAM/Usage:Net/Rate"`);
  const metrics: VMMetrics = {};
  
  const lines = stdout.split('\n');
  for (const line of lines) {
    if (line.includes('CPU/Load')) {
      const match = line.match(/CPU\/Load.*?(\d+\.?\d*%)/);
      if (match) metrics.cpuLoad = match[1];
    }
    if (line.includes('RAM/Usage')) {
      const match = line.match(/RAM\/Usage.*?(\d+\.?\d*\s*[KMG]?B)/);
      if (match) metrics.ramUsage = match[1];
    }
    if (line.includes('Net/Rate')) {
      const match = line.match(/Net\/Rate.*?(\d+\.?\d*\s*[KMG]?B\/s)/);
      if (match) metrics.netRate = match[1];
    }
  }
  
  return metrics;
}

// ============================================
// Export/Import
// ============================================

/**
 * Export VM to OVA
 */
export async function exportVM(vmName: string, outputPath: string): Promise<void> {
  await vboxCommand(`export "${vmName}" --output "${outputPath}"`);
}

/**
 * Import VM from OVA
 */
export async function importVM(ovaPath: string, vmName?: string): Promise<void> {
  const nameOption = vmName ? `--vsys 0 --vmname "${vmName}"` : '';
  await vboxCommand(`import "${ovaPath}" ${nameOption}`);
}

// ============================================
// Utility Functions
// ============================================

/**
 * Wait for VM to reach a specific state
 */
export async function waitForState(
  vmName: string,
  targetState: 'running' | 'powered off' | 'saved' | 'paused',
  timeout: number = 60000
): Promise<boolean> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const info = await getVMInfo(vmName);
    const state = info.VMState || '';
    
    if (targetState === 'running' && state === 'running') return true;
    if (targetState === 'powered off' && state === 'poweroff') return true;
    if (targetState === 'saved' && state === 'saved') return true;
    if (targetState === 'paused' && state === 'paused') return true;
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  return false;
}

/**
 * Safe shutdown with timeout
 */
export async function safeShutdown(vmName: string, timeout: number = 30000): Promise<boolean> {
  await stopVM(vmName);
  const success = await waitForState(vmName, 'powered off', timeout);
  
  if (!success) {
    console.log('Graceful shutdown timed out, forcing power off...');
    await forceStopVM(vmName);
    return await waitForState(vmName, 'powered off', 10000);
  }
  
  return true;
}

/**
 * Get VBoxManage version
 */
export async function getVersion(): Promise<string> {
  const { stdout } = await vboxCommand('--version');
  return stdout.trim();
}

/**
 * List available OS types
 */
export async function listOSTypes(): Promise<{ id: string; description: string }[]> {
  const { stdout } = await vboxCommand('list ostypes');
  const types: { id: string; description: string }[] = [];
  
  const lines = stdout.split('\n');
  let currentId = '';
  let currentDesc = '';
  
  for (const line of lines) {
    const idMatch = line.match(/^ID:\s+(.+)$/);
    const descMatch = line.match(/^Description:\s+(.+)$/);
    
    if (idMatch) {
      currentId = idMatch[1];
    }
    if (descMatch) {
      currentDesc = descMatch[1];
      if (currentId) {
        types.push({ id: currentId, description: currentDesc });
        currentId = '';
        currentDesc = '';
      }
    }
  }
  
  return types;
}

// Export all functions
export default {
  listVMs,
  listRunningVMs,
  getVMInfo,
  vmExists,
  isVMRunning,
  startVM,
  stopVM,
  forceStopVM,
  pauseVM,
  resumeVM,
  resetVM,
  saveVMState,
  createVM,
  deleteVM,
  cloneVM,
  listSnapshots,
  takeSnapshot,
  restoreSnapshot,
  deleteSnapshot,
  configureNetwork,
  addPortForward,
  removePortForward,
  listHostOnlyInterfaces,
  setMemory,
  setCPUs,
  configurePerformance,
  setupMetrics,
  queryMetrics,
  exportVM,
  importVM,
  waitForState,
  safeShutdown,
  getVersion,
  listOSTypes
};
