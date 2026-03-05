#!/usr/bin/env node
/**
 * GCP Resource Scanner
 *
 * Usage: node gcp-scanner.js [--project <id>] [--region <region>] [--output <format>] <resource-type>...
 *
 * Example:
 *   node gcp-scanner.js --project my-gcp-project --region us-central1 compute subnet --output json
 *   node gcp-scanner.js compute
 *
 * Supported resource types:
 *   compute    - Compute Engine instances
 *   network    - VPC networks
 *   subnet     - Subnets
 *   disk       - Persistent disks
 *   firewall   - Firewall rules
 *   gke        - GKE clusters
 *   cloudsql   - Cloud SQL instances
 *   gcr        - Container Registry images (list only, metadata limited)
 *
 * Outputs JSON array to stdout with resource metadata:
 * [
 *   {
 *     "type": "google_compute_instance",
 *     "id": "projects/.../zones/.../instances/myvm",
 *     "name": "myvm",
 *     "project": "my-project",
 *     "zone": "us-central1-a",
 *     "attributes": { ... },
 *     "labels": { ... }
 *   }
 * ]
 */

const { Compute } = require('@google-cloud/compute');
const { ResourceManager } = require('@google-cloud/resource-manager');
const { SQL } = require('@google-cloud/sql');
const { ContainerAnalysisClient } = require('@google-cloud/containeranalysis').v1;
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('project', {
    alias: 'p',
    type: 'string',
    description: 'GCP project ID',
    default: process.env.GCP_PROJECT || process.env.GOOGLE_CLOUD_PROJECT
  })
  .option('region', {
    alias: 'r',
    type: 'string',
    description: 'GCP region to scan (for regional resources)'
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
const projectId = argv.project;
const region = argv.region;
const outputFormat = argv.output;

/**
 * Get all zones for the project if needed
 */
async function listZones(compute) {
  const [zones] = await compute.getZones();
  return zones;
}

/**
 * Scan Compute Engine instances
 */
async function scanCompute() {
  const results = [];

  try {
    const compute = new Compute();
    const zones = await listZones(compute);

    // If region specified, filter zones
    const targetZones = region
      ? zones.filter(z => z.name.startsWith(region))
      : zones;

    for (const zone of targetZones) {
      console.error(`Scanning instances in zone ${zone.name}...`);
      const instances = zone.getInstances();

      for await (const instance of instances) {
        results.push({
          type: 'google_compute_instance',
          id: instance.id,
          name: instance.name,
          project: projectId,
          zone: zone.name,
          region: zone.region?.name,
          attributes: {
            machine_type: instance.machineType,
            status: instance.status,
            cpu_platform: instance.cpuPlatform,
            disks: instance.disks?.map(d => ({
              device_name: d.deviceName,
              boot: d.boot,
              auto_delete: d.autoDelete,
              initialize_params: d.initializeParams
            })),
            network_interfaces: instance.networkInterfaces?.map(ni => ({
              network: ni.network,
              subnetwork: ni.subnetwork,
              access_configs: ni.accessConfigs
            })),
            service_accounts: instance.serviceAccounts
          },
          labels: instance.labels || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Compute instances: ${err.message}`);
  }

  return results;
}

/**
 * Scan VPC networks
 */
async function scanNetwork() {
  const results = [];

  try {
    const compute = new Compute();
    const [networks] = await compute.getNetworks();

    for (const network of networks) {
      const [metadata] = await network.getMetadata();
      results.push({
        type: 'google_compute_network',
        id: network.id,
        name: network.name,
        project: projectId,
        attributes: {
          routing_config: network.routingConfig,
          auto_create_subnetworks: metadata?.autoCreateSubnetworks,
          ipv4_range: metadata?.ipv4Range
        },
        labels: network.labels || {}
      });
    }
  } catch (err) {
    console.error(`Error scanning Networks: ${err.message}`);
  }

  return results;
}

/**
 * Scan Subnets
 */
async function scanSubnet() {
  const results = [];

  try {
    const compute = new Compute();
    const [subnets] = await compute.getSubnetworks();

    // Filter by region if specified
    const targetSubnets = region
      ? subnets.filter(s => s.region?.endsWith(region))
      : subnets;

    for (const subnet of targetSubnets) {
      results.push({
        type: 'google_compute_subnetwork',
        id: subnet.id,
        name: subnet.name,
        project: projectId,
        region: subnet.region,
        attributes: {
          network: subnet.network,
          ip_cidr_range: subnet.ipCidrRange,
          private_ip_google_access: subnet.privateIpGoogleAccess,
          secondary_ip_ranges: subnet.secondaryIpRanges
        },
        labels: subnet.labels || {}
      });
    }
  } catch (err) {
    console.error(`Error scanning Subnets: ${err.message}`);
  }

  return results;
}

/**
 * Scan Persistent Disks
 */
async function scanDisk() {
  const results = [];

  try {
    const compute = new Compute();
    const zones = await listZones(compute);

    // If region specified, filter zones
    const targetZones = region
      ? zones.filter(z => z.name.startsWith(region))
      : zones;

    for (const zone of targetZones) {
      console.error(`Scanning disks in zone ${zone.name}...`);
      const disks = zone.getDisks();

      for await (const disk of disks) {
        results.push({
          type: 'google_compute_disk',
          id: disk.id,
          name: disk.name,
          project: projectId,
          zone: zone.name,
          region: zone.region?.name,
          attributes: {
            size_gb: disk.sizeGb,
            disk_type: disk.type,
            status: disk.status,
            source_snapshot: disk.sourceSnapshot,
            source_image: disk.sourceImage
          },
          labels: disk.labels || {}
        });
      }
    }
  } catch (err) {
    console.error(`Error scanning Disks: ${err.message}`);
  }

  return results;
}

/**
 * Scan Firewall Rules
 */
async function scanFirewall() {
  const results = [];

  try {
    const compute = new Compute();
    const [firewalls] = await compute.getFirewalls();

    for (const fw of firewalls) {
      results.push({
        type: 'google_compute_firewall',
        id: fw.id,
        name: fw.name,
        project: projectId,
        attributes: {
          network: fw.network,
          direction: fw.direction,
          priority: fw.priority,
          source_ranges: fw.sourceRanges,
          destination_ranges: fw.destinationRanges,
          allowed: fw.allowed,
          denied: fw.denied
        },
        labels: fw.labels || {}
      });
    }
  } catch (err) {
    console.error(`Error scanning Firewalls: ${err.message}`);
  }

  return results;
}

/**
 * Scan GKE clusters
 */
async function scanGKE() {
  const { KubernetesEngineClient } = require('@google-cloud/container').v1;
  const results = [];

  try {
    const client = new KubernetesEngineClient();
    const parent = `projects/${projectId}/locations/-`; // All locations

    const [clusters] = await client.listClusters({ parent });

    for (const cluster of clusters) {
      results.push({
        type: 'google_container_cluster',
        id: cluster.name,
        name: cluster.name,
        project: projectId,
        location: cluster.location,
        attributes: {
          initial_cluster_version: cluster.initialClusterVersion,
          current_master_version: cluster.currentMasterVersion,
          node_config: cluster.nodeConfig,
          network: cluster.network,
          subnetwork: cluster.subnetwork,
          ip_allocation_policy: cluster.ipAllocationPolicy,
          private_cluster_config: cluster.privateClusterConfig,
          master_auth: cluster.masterAuth
        },
        labels: cluster.labelFingerprint || {}
      });
    }
  } catch (err) {
    console.error(`Error scanning GKE clusters: ${err.message}`);
  }

  return results;
}

/**
 * Scan Cloud SQL instances
 */
async function scanCloudSQL() {
  const results = [];

  try {
    const sql = new SQL();
    const [instances] = await sql.getInstances(projectId);

    for (const instance of instances) {
      results.push({
        type: 'google_sql_database_instance',
        id: instance.name,
        name: instance.name,
        project: projectId,
        region: instance.region,
        attributes: {
          database_version: instance.databaseVersion,
          tier: instance.tier,
          state: instance.state,
          root_password_set: instance.rootPasswordSet || false,
          ip_addresses: instance.ipAddresses,
          settings: instance.settings
        },
        labels: instance.labels || {}
      });
    }
  } catch (err) {
    console.error(`Error scanning Cloud SQL: ${err.message}`);
  }

  return results;
}

/**
 * Scan Container Registry images (basic listing)
 */
async function scanGCR() {
  const { ContainerAnalysisClient } = require('@google-cloud/containeranalysis').v1;
  const results = [];

  try {
    // GCR images are stored in Artifact Registry or Container Registry
    // Full metadata requires scanning multiple projects; we'll do a basic scan
    // For full listing, gcloud or direct registry API calls would be needed

    console.error('GCR scanning limited - consider using artifact registry API for full lists');
    results.push({
      type: 'google_container_registry_repository',
      id: `projects/${projectId}/repositories`,
      name: 'gcr.io',
      project: projectId,
      region: 'global',
      attributes: {
        note: 'Full GCR image listing requires artifact registry API per-repository scanning'
      },
      labels: {}
    });
  } catch (err) {
    console.error(`Error scanning GCR: ${err.message}`);
  }

  return results;
}

/**
 * Resource scanner dispatcher
 */
const scanners = {
  compute: scanCompute,
  instance: scanCompute,
  vm: scanCompute,
  network: scanNetwork,
  vpc: scanNetwork,
  subnet: scanSubnet,
  disk: scanDisk,
  firewall: scanFirewall,
  gke: scanGKE,
  kubernetes: scanGKE,
  cloudsql: scanCloudSQL,
  sql: scanCloudSQL,
  gcr: scanGCR,
  registry: scanGCR
};

/**
 * Main entry
 */
async function main() {
  console.error(`GCP Resource Scanner (project: ${projectId}, region: ${region || 'all'})`);

  if (!projectId) {
    console.error('Error: GCP project ID is required');
    console.error('Set GCP_PROJECT environment variable or use --project <id>');
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
      `[${r.type}] ${r.name} in ${r.zone || r.location || r.region || 'unknown'}`
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

module.exports = { scanCompute, scanNetwork, scanSubnet, scanDisk, scanFirewall, scanGKE, scanCloudSQL };
