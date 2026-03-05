#!/usr/bin/env node
/**
 * Azure Resource Scanner
 *
 * Usage: node azure-scanner.js [--subscription <id>] [--location <region>] [--output <format>] <resource-type>...
 *
 * Example:
 *   node azure-scanner.js --location eastus vm vnet subnet --output json
 *   node azure-scanner.js vm
 *
 * Supported resource types:
 *   vm        - Virtual Machines
 *   vnet      - Virtual Networks
 *   subnet    - Subnets
 *   nic       - Network Interfaces
 *   pip       - Public IP Addresses
 *   disk      - Managed Disks
 *   nsg       - Network Security Groups
 *   lb        - Load Balancers
 *   appsvc    - App Services
 *
 * Outputs JSON array to stdout with resource metadata:
 * [
 *   {
 *     "type": "azurerm_virtual_machine",
 *     "id": "/subscriptions/.../resourceGroups/.../providers/Microsoft.Compute/virtualMachines/myvm",
 *     "name": "myvm",
 *     "resource_group": "my-rg",
 *     "location": "eastus",
 *     "attributes": { ... },
 *     "tags": { ... }
 *   }
 * ]
 */

const { DefaultAzureCredential } = require('@azure/identity');
const {
  ComputeManagementClient,
  VirtualMachines
} = require('@azure/arm-compute');
const {
  NetworkManagementClient,
  VirtualNetworks,
  Subnets,
  NetworkInterfaces,
  PublicIPAddresses,
  NetworkSecurityGroups
} = require('@azure/arm-network');
const {
  ResourceManagementClient,
  Resources
} = require('@azure/arm-resources');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('subscription', {
    alias: 's',
    type: 'string',
    description: 'Azure subscription ID',
    default: process.env.AZURE_SUBSCRIPTION_ID
  })
  .option('location', {
    alias: 'l',
    type: 'string',
    description: 'Azure location/region to scan'
  })
  .option('output', {
    alias: 'o',
    type: 'string',
    default: 'json',
    choices: ['json', 'text']
  })
  .demandCommand(1, 'At least one resource type is required')
  .argv;

const resourceTypes = argv._;
const subscriptionId = argv.subscription;
const location = argv.location || process.env.AZURE_LOCATION;
const outputFormat = argv.output;

/**
 * Create authenticated Azure clients
 */
let computeClient, networkClient, resourceClient;

async function initClients() {
  const credential = new DefaultAzureCredential();

  computeClient = new ComputeManagementClient(credential, subscriptionId);
  networkClient = new NetworkManagementClient(credential, subscriptionId);
  resourceClient = new ResourceManagementClient(credential, subscriptionId);
}

/**
 * List all resource groups (optionally filtered by location)
 */
async function listResourceGroups() {
  const rgs = [];
  const iterator = resourceClient.resourceGroups.list();
  for await (const rg of iterator) {
    if (!location || rg.location === location) {
      rgs.push(rg);
    }
  }
  return rgs;
}

/**
 * Scan Virtual Machines
 */
async function scanVM() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = computeClient.virtualMachines.list(rg.name);
      for await (const vm of iterator) {
        results.push({
          type: 'azurerm_virtual_machine',
          id: vm.id,
          name: vm.name,
          resource_group: rg.name,
          location: vm.location,
          attributes: {
            vm_size: vm.hardwareProfile?.vmSize,
            os_type: vm.storageProfile?.osDisk?.osType,
            admin_username: vm.osProfile?.adminUsername,
            computer_name: vm.osProfile?.computerName,
            provisioning_state: vm.provisioningState
          },
          tags: vm.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning VMs: ${err.message}`);
  }

  return results;
}

/**
 * Scan Virtual Networks
 */
async function scanVNet() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.virtualNetworks.list(rg.name);
      for await (const vnet of iterator) {
        results.push({
          type: 'azurerm_virtual_network',
          id: vnet.id,
          name: vnet.name,
          resource_group: rg.name,
          location: vnet.location,
          attributes: {
            address_space: vnet.addressSpace?.addressPrefixes,
            dns_servers: vnet.dhcpOptions?.dnsServers
          },
          tags: vnet.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning VNets: ${err.message}`);
  }

  return results;
}

/**
 * Scan Subnets
 */
async function scanSubnet() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.subnets.list(rg.name);
      for await (const subnet of iterator) {
        results.push({
          type: 'azurerm_subnet',
          id: subnet.id,
          name: subnet.name,
          resource_group: rg.name,
          location: subnet.location,
          attributes: {
            address_prefix: subnet.addressPrefix,
            security_group_id: subnet.networkSecurityGroup?.id,
            route_table_id: subnet.routeTable?.id,
            service_endpoints: subnet.serviceEndpoints
          },
          tags: subnet.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Subnets: ${err.message}`);
  }

  return results;
}

/**
 * Scan Network Interfaces
 */
async function scanNIC() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.networkInterfaces.list(rg.name);
      for await (const nic of iterator) {
        results.push({
          type: 'azurerm_network_interface',
          id: nic.id,
          name: nic.name,
          resource_group: rg.name,
          location: nic.location,
          attributes: {
            ip_configurations: nic.ipConfigurations?.map(ipc => ({
              name: ipc.name,
              private_ip_address: ipc.privateIPAddress,
              private_ip_allocation_method: ipc.privateIPAllocationMethod,
              public_ip_address_id: ipc.publicIPAddress?.id,
              subnet_id: ipc.subnet?.id
            })),
            enable_ip_forwarding: nic.enableIPForwarding,
            network_security_group_id: nic.networkSecurityGroup?.id
          },
          tags: nic.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning NICs: ${err.message}`);
  }

  return results;
}

/**
 * Scan Public IP Addresses
 */
async function scanPublicIP() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.publicIPAddresses.list(rg.name);
      for await (const pip of iterator) {
        results.push({
          type: 'azurerm_public_ip',
          id: pip.id,
          name: pip.name,
          resource_group: rg.name,
          location: pip.location,
          attributes: {
            public_ip_address: pip.ipAddress,
            public_ip_allocation_method: pip.publicIPAllocationMethod,
            sku: pip.sku?.name,
            domain_name_label: pip.dnsSettings?.domainNameLabel,
            fqdn: pip.dnsSettings?.fqdn
          },
          tags: pip.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Public IPs: ${err.message}`);
  }

  return results;
}

/**
 * Scan Managed Disks
 */
async function scanDisk() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = computeClient.disks.list(rg.name);
      for await (const disk of iterator) {
        results.push({
          type: 'azurerm_managed_disk',
          id: disk.id,
          name: disk.name,
          resource_group: rg.name,
          location: disk.location,
          attributes: {
            disk_size_gb: disk.diskSizeGB,
            disk_type: disk.sku?.name,
            os_type: disk.osType,
            provisioning_state: disk.provisioningState
          },
          tags: disk.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Disks: ${err.message}`);
  }

  return results;
}

/**
 * Scan Network Security Groups
 */
async function scanNSG() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.networkSecurityGroups.list(rg.name);
      for await (const nsg of iterator) {
        results.push({
          type: 'azurerm_network_security_group',
          id: nsg.id,
          name: nsg.name,
          resource_group: rg.name,
          location: nsg.location,
          attributes: {
            security_rules: nsg.securityRules?.map(rule => ({
              name: rule.name,
              priority: rule.priority,
              direction: rule.direction,
              access: rule.access,
              protocol: rule.protocol,
              source_port_range: rule.sourcePortRange,
              destination_port_range: rule.destinationPortRange,
              source_address_prefix: rule.sourceAddressPrefix,
              destination_address_prefix: rule.destinationAddressPrefix
            }))
          },
          tags: nsg.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning NSGs: ${err.message}`);
  }

  return results;
}

/**
 * Scan Load Balancers
 */
async function scanLB() {
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = networkClient.loadBalancers.list(rg.name);
      for await (const lb of iterator) {
        results.push({
          type: 'azurerm_lb',
          id: lb.id,
          name: lb.name,
          resource_group: rg.name,
          location: lb.location,
          attributes: {
            sku: lb.sku?.name,
            frontend_ip_configurations: lb.frontendIPConfigurations?.map(fic => ({
              name: fic.name,
              public_ip_address_id: fic.publicIPAddress?.id,
              private_ip_address: fic.privateIPAddress,
              subnet_id: fic.subnet?.id
            })),
            backend_address_pools: lb.backendAddressPools?.map(bap => ({
              name: bap.name
            }))
          },
          tags: lb.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Load Balancers: ${err.message}`);
  }

  return results;
}

/**
 * Scan App Services (Web Apps)
 */
async function scanAppService() {
  const { WebSiteManagementClient } = require('@azure/arm-appservice');
  const client = new WebSiteManagementClient(subscriptionId, new DefaultAzureCredential());
  const results = [];

  try {
    const rgs = await listResourceGroups();
    for (const rg of rgs) {
      const iterator = client.webApps.listByResourceGroup(rg.name);
      for await (const app of iterator) {
        results.push({
          type: 'azurerm_linux_web_app',
          id: app.id,
          name: app.name,
          resource_group: rg.name,
          location: app.location,
          attributes: {
            server_farm_id: app.serverFarmId,
            site_config: app.siteConfig,
            https_only: app.httpsOnly
          },
          tags: app.tags || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning App Services: ${err.message}`);
  }

  return results;
}

/**
 * Resource scanner dispatcher
 */
const scanners = {
  vm: scanVM,
  vnet: scanVNet,
  subnet: scanSubnet,
  nic: scanNIC,
  pip: scanPublicIP,
  public_ip: scanPublicIP,
  disk: scanDisk,
  nsg: scanNSG,
  lb: scanLB,
  appsvc: scanAppService,
  app_service: scanAppService,
  webapp: scanAppService
};

/**
 * Main entry
 */
async function main() {
  console.error(`Azure Resource Scanner (subscription: ${subscriptionId}, location: ${location || 'all'})`);

  try {
    await initClients();
  } catch (err) {
    console.error(`Failed to authenticate with Azure: ${err.message}`);
    console.error('Ensure AZURE_SUBSCRIPTION_ID is set and credentials are configured');
    process.exit(1);
  }

  const allResources = [];

  for (const resourceType of resourceTypes) {
    const scanner = scanners[resourceType];
    if (!scanner) {
      console.error(`Warning: Unknown resource type '${resourceType}'. Skipping.`);
      continue;
    }

    console.error(`Scanning ${resourceType}...`);
    try {
      const resources = await scanner();
      allResources.push(...resources);
    } catch (err) {
      console.error(`Failed to scan ${resourceType}: ${err.message}`);
    }
  }

  // Output results
  if (outputFormat === 'json') {
    console.log(JSON.stringify(allResources, null, 2));
  } else {
    console.log(allResources.map(r =>
      `[${r.type}] ${r.name} (RG: ${r.resource_group}) in ${r.location}`
    ).join('\\n'));
  }

  process.exit(0);
}

if (require.main === module) {
  main().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = { scanVM, scanVNet, scanSubnet, scanNIC, scanPublicIP, scanDisk, scanNSG, scanLB, scanAppService };
