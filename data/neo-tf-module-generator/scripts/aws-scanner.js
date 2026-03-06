#!/usr/bin/env node
/**
 * AWS Resource Scanner
 *
 * Usage: node aws-scanner.js [--region <region>] [--output <format>] <resource-type>...
 *
 * Example:
 *   node aws-scanner.js --region us-east-1 ec2 vpc subnet --output json
 *   node aws-scanner.js ec2
 *
 * Supported resource types:
 *   ec2        - EC2 instances
 *   vpc        - Virtual Private Clouds
 *   subnet     - Subnets
 *   rds        - RDS databases
 *   s3         - S3 buckets
 *   lambda     - Lambda functions
 *   sg         - Security groups
 *
 * Outputs JSON array to stdout with resource metadata:
 * [
 *   {
 *     "type": "aws_instance",
 *     "id": "i-1234567890abcdef0",
 *     "name": "my-server",
 *     "region": "us-east-1",
 *     "attributes": { ... },
 *     "tags": { ... }
 *   }
 * ]
 */

const { EC2Client, DescribeInstancesCommand, DescribeVpcsCommand, DescribeSubnetsCommand,
        DescribeSecurityGroupsCommand, DescribeRouteTablesCommand, DescribeInternetGatewaysCommand,
        DescribeNatGatewaysCommand, DescribeVolumesCommand } = require('@aws-sdk/client-ec2');
const { S3Client, ListBucketsCommand } = require('@aws-sdk/client-s3');
const { RDSClient, DescribeDBInstancesCommand } = require('@aws-sdk/client-rds');
const { LambdaClient, ListFunctionsCommand } = require('@aws-sdk/client-lambda');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('region', {
    alias: 'r',
    type: 'string',
    description: 'AWS region to scan'
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
const region = argv.region || process.env.AWS_REGION || 'us-east-1';
const outputFormat = argv.output;

/**
 * Create AWS client with region
 */
function createClient(Service) {
  return new Service({
    region,
    // Credentials from environment/chain automatically
  });
}

/**
 * Scan EC2 instances
 */
async function scanEC2() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeInstancesCommand({
        MaxResults: 1000,
        NextToken: nextToken
      });
      const resp = await client.send(cmd);

      for (const reservation of resp.Reservations || []) {
        for (const instance of reservation.Instances || []) {
          const nameTag = instance.Tags?.find(t => t.Key === 'Name');
          results.push({
            type: 'aws_instance',
            id: instance.InstanceId,
            name: nameTag?.Value || instance.InstanceId,
            region,
            attributes: {
              instance_type: instance.InstanceType,
              state: instance.State?.Name,
              image_id: instance.ImageId,
              availability_zone: instance.Placement?.AvailabilityZone,
              private_ip: instance.PrivateIpAddress,
              public_ip: instance.PublicIpAddress,
              launch_time: instance.LaunchTime
            },
            tags: instance.Tags?.reduce((acc, tag) => {
              acc[tag.Key] = tag.Value;
              return acc;
            }, {}) || {}
          });
        }
        nextToken = resp.NextToken;
      }
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning EC2: ${err.message}`);
  }

  return results;
}

/**
 * Scan VPCs
 */
async function scanVPC() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeVpcsCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const vpc of resp.Vpcs || []) {
        const nameTag = vpc.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_vpc',
          id: vpc.VpcId,
          name: nameTag?.Value || vpc.VpcId,
          region,
          attributes: {
            cidr_block: vpc.CidrBlock,
            state: vpc.State,
            is_default: vpc.IsDefault
          },
          tags: vpc.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning VPCs: ${err.message}`);
  }

  return results;
}

/**
 * Scan Subnets
 */
async function scanSubnet() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeSubnetsCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const subnet of resp.Subnets || []) {
        const nameTag = subnet.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_subnet',
          id: subnet.SubnetId,
          name: nameTag?.Value || subnet.SubnetId,
          region,
          attributes: {
            vpc_id: subnet.VpcId,
            cidr_block: subnet.CidrBlock,
            availability_zone: subnet.AvailabilityZone,
            state: subnet.State,
            map_public_ip_on_launch: subnet.MapPublicIpOnLaunch
          },
          tags: subnet.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning Subnets: ${err.message}`);
  }

  return results;
}

/**
 * Scan Security Groups
 */
async function scanSecurityGroups() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeSecurityGroupsCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const sg of resp.SecurityGroups || []) {
        const nameTag = sg.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_security_group',
          id: sg.GroupId,
          name: nameTag?.Value || sg.GroupName,
          region,
          attributes: {
            description: sg.Description,
            vpc_id: sg.VpcId,
            group_name: sg.GroupName,
            ip_permissions: sg.IpPermissions,
            ip_permissions_egress: sg.IpPermissionsEgress
          },
          tags: sg.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning Security Groups: ${err.message}`);
  }

  return results;
}

/**
 * Scan RDS instances
 */
async function scanRDS() {
  const client = createClient(RDSClient);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeDBInstancesCommand({ MaxRecords: 100, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const db of resp.DBInstances || []) {
        results.push({
          type: 'aws_db_instance',
          id: db.DBInstanceIdentifier,
          name: db.DBInstanceIdentifier,
          region,
          attributes: {
            engine: db.Engine,
            engine_version: db.EngineVersion,
            instance_class: db.DBInstanceClass,
            allocated_storage: db.AllocatedStorage,
            storage_type: db.StorageType,
            multi_az: db.MultiAZ,
            publicly_accessible: db.PubliclyAccessible,
            availability_zone: db.AvailabilityZone,
            status: db.DBInstanceStatus
          },
          tags: (await client.send(new RDSClient.ListTagsForResourceCommand({
            ResourceName: db.DBInstanceArn
          }))).TagList?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
        nextToken = resp.NextToken;
      }
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning RDS: ${err.message}`);
  }

  return results;
}

/**
 * Scan S3 buckets (global, not regional)
 */
async function scanS3() {
  const client = createClient(S3Client);
  const results = [];

  try {
    const cmd = new ListBucketsCommand({});
    const resp = await client.send(cmd);

    for (const bucket of resp.Buckets || []) {
      // Get bucket location
      let bucketRegion = 'us-east-1';
      try {
        const locResp = await client.send(new S3Client.GetBucketLocationCommand({
          Bucket: bucket.Name
        }));
        bucketRegion = locResp.LocationConstraint || 'us-east-1';
      } catch (e) {
        // Ignore location errors (permissions)
      }

      results.push({
        type: 'aws_s3_bucket',
        id: bucket.Name,
        name: bucket.Name,
        region: bucketRegion,
        attributes: {
          creation_date: bucket.CreationDate
        },
        tags: {} // Would require additional API calls per bucket
      });
    }
  } catch (err) {
    console.error(`Error scanning S3: ${err.message}`);
  }

  return results;
}

/**
 * Scan Lambda functions
 */
async function scanLambda() {
  const { LambdaClient, ListFunctionsCommand } = require('@aws-sdk/client-lambda');
  const client = createClient(LambdaClient);
  const results = [];

  try {
    let nextMarker;
    do {
      const cmd = new ListFunctionsCommand({
        MaxItems: 1000,
        Marker: nextMarker
      });
      const resp = await client.send(cmd);

      for (const fn of resp.Functions || []) {
        results.push({
          type: 'aws_lambda_function',
          id: fn.FunctionName,
          name: fn.FunctionName,
          region,
          attributes: {
            runtime: fn.Runtime,
            handler: fn.Handler,
            code_size: fn.CodeSize,
            description: fn.Description,
            timeout: fn.Timeout,
            memory_size: fn.MemorySize,
            last_modified: fn.LastModified,
            revision_id: fn.RevisionId
          },
          tags: fn.Tags || {}
        });
      }
      nextMarker = resp.NextMarker;
    } while (nextMarker);
  } catch (err) {
    console.error(`Error scanning Lambda: ${err.message}`);
  }

  return results;
}

/**
 * Scan Route Tables (additional network resource)
 */
async function scanRouteTables() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeRouteTablesCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const rt of resp.RouteTables || []) {
        const nameTag = rt.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_route_table',
          id: rt.RouteTableId,
          name: nameTag?.Value || rt.RouteTableId,
          region,
          attributes: {
            vpc_id: rt.VpcId,
            routes: rt.Routes,
            associations: rt.Associations
          },
          tags: rt.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning Route Tables: ${err.message}`);
  }

  return results;
}

/**
 * Scan Internet Gateways
 */
async function scanInternetGateways() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeInternetGatewaysCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const igw of resp.InternetGateways || []) {
        const nameTag = igw.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_internet_gateway',
          id: igw.InternetGatewayId,
          name: nameTag?.Value || igw.InternetGatewayId,
          region,
          attributes: {
            attachments: igw.Attachments
          },
          tags: igw.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning Internet Gateways: ${err.message}`);
  }

  return results;
}

/**
 * Scan NAT Gateways
 */
async function scanNatGateways() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeNatGatewaysCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const nat of resp.NatGateways || []) {
        const nameTag = nat.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_nat_gateway',
          id: nat.NatGatewayId,
          name: nameTag?.Value || nat.NatGatewayId,
          region,
          attributes: {
            subnet_id: nat.SubnetId,
            connectivity_type: nat.ConnectivityType,
            state: nat.State,
            private_ip: nat.PrivateIp,
            public_ips: nat.PublicIpAddresses
          },
          tags: nat.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextMarker;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning NAT Gateways: ${err.message}`);
  }

  return results;
}

/**
 * Scan EBS volumes
 */
async function scanVolumes() {
  const client = createClient(EC2Client);
  const results = [];

  try {
    let nextToken;
    do {
      const cmd = new DescribeVolumesCommand({ MaxResults: 1000, NextToken: nextToken });
      const resp = await client.send(cmd);

      for (const vol of resp.Volumes || []) {
        const nameTag = vol.Tags?.find(t => t.Key === 'Name');
        results.push({
          type: 'aws_ebs_volume',
          id: vol.VolumeId,
          name: nameTag?.Value || vol.VolumeId,
          region,
          attributes: {
            size: vol.Size,
            volume_type: vol.VolumeType,
            state: vol.State,
            iops: vol.Iops,
            encrypted: vol.Encrypted,
            snapshot_id: vol.SnapshotId,
            availability_zone: vol.AvailabilityZone
          },
          tags: vol.Tags?.reduce((acc, tag) => {
            acc[tag.Key] = tag.Value;
            return acc;
          }, {}) || {}
        });
      }
      nextToken = resp.NextToken;
    } while (nextToken);
  } catch (err) {
    console.error(`Error scanning EBS Volumes: ${err.message}`);
  }

  return results;
}

/**
 * Resource scanner dispatcher
 */
const scanners = {
  ec2: scanEC2,
  vpc: scanVPC,
  subnet: scanSubnet,
  sg: scanSecurityGroups,
  security_group: scanSecurityGroups,
  rds: scanRDS,
  s3: scanS3,
  lambda: scanLambda,
  route_table: scanRouteTables,
  rt: scanRouteTables,
  igw: scanInternetGateways,
  internet_gateway: scanInternetGateways,
  nat: scanNatGateways,
  nat_gateway: scanNatGateways,
  volume: scanVolumes,
  ebs: scanVolumes
};

/**
 * Main entry
 */
async function main() {
  console.error(`AWS Resource Scanner (region: ${region})`);

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
      `[${r.type}] ${r.name} (${r.id}) in ${r.region}`
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

module.exports = { scanEC2, scanVPC, scanSubnet, scanSecurityGroups, scanRDS, scanS3, scanLambda };
