#!/usr/bin/env node
import crypto from "crypto";
import https from "https";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadConfig() {
  const configPath = path.join(__dirname, "..", "config.json");
  if (fs.existsSync(configPath)) {
    try {
      return JSON.parse(fs.readFileSync(configPath, "utf-8"));
    } catch {
      console.warn("Failed to parse config.json, using defaults.");
    }
  }
  return {};
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true;
      args[key] = val;
    }
  }
  return args;
}

const config = loadConfig();
const args = parseArgs(process.argv);

const service = args.service;
const metric = args.metric;
const resource = args.resource;
const hours = args.hours ? Number(args.hours) : config.defaultHours ?? 1;
const period = args.period ? Number(args.period) : config.defaultPeriod ?? 300;
const region = args.region || process.env.AWS_REGION || config.defaultRegion || "us-west-2";
const serviceName = args.serviceName;
const debug = !!args.debug;

if (!service || !metric || !resource) {
  console.log("Usage: node src/cli.mjs --service <ecs|ec2|rds> --metric <metric> --resource <id> [--serviceName <ecs-service>] [--hours 1] [--period 300] [--region us-west-2] [--debug]");
  process.exit(1);
}

const metricMap = {
  ecs: {
    namespace: "AWS/ECS",
    dimensions: (name) => [{ Name: "ClusterName", Value: name }],
  },
  ec2: {
    namespace: "AWS/EC2",
    dimensions: (id) => [{ Name: "InstanceId", Value: id }],
  },
  rds: {
    namespace: "AWS/RDS",
    dimensions: (id) => [{ Name: "DBInstanceIdentifier", Value: id }],
  },
};

const aliasTable = config.metricAliases || {};
const resolvedMetric = aliasTable?.[service]?.[metric] || metric;
const knownAliases = Object.keys(aliasTable?.[service] || {});

const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;
if (!accessKeyId || !secretAccessKey) {
  console.error("Missing AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY");
  process.exit(1);
}

const endTime = new Date();
const startTime = new Date(endTime.getTime() - hours * 60 * 60 * 1000);

function toAmzDate(date) {
  return date.toISOString().replace(/[:-]|\..*/g, "") + "Z";
}

function toDateStamp(date) {
  return date.toISOString().slice(0, 10).replace(/-/g, "");
}

function hmac(key, data, encoding) {
  return crypto.createHmac("sha256", key).update(data, "utf8").digest(encoding);
}

function sha256(data, encoding = "hex") {
  return crypto.createHash("sha256").update(data, "utf8").digest(encoding);
}

function getSignatureKey(key, dateStamp, regionName, serviceName) {
  const kDate = hmac("AWS4" + key, dateStamp);
  const kRegion = hmac(kDate, regionName);
  const kService = hmac(kRegion, serviceName);
  const kSigning = hmac(kService, "aws4_request");
  return kSigning;
}

function buildQuery(params) {
  return Object.keys(params)
    .sort()
    .map((k) => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
    .join("&");
}

async function signedRequest({ host, region, service, params }) {
  const method = "GET";
  const canonicalUri = "/";
  const amzDate = toAmzDate(new Date());
  const dateStamp = toDateStamp(new Date());

  const canonicalQuerystring = buildQuery(params);
  const canonicalHeaders = `host:${host}\n` + `x-amz-date:${amzDate}\n`;
  const signedHeaders = "host;x-amz-date";
  const payloadHash = sha256("");
  const canonicalRequest = [
    method,
    canonicalUri,
    canonicalQuerystring,
    canonicalHeaders,
    signedHeaders,
    payloadHash,
  ].join("\n");

  const algorithm = "AWS4-HMAC-SHA256";
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = [
    algorithm,
    amzDate,
    credentialScope,
    sha256(canonicalRequest),
  ].join("\n");

  const signingKey = getSignatureKey(secretAccessKey, dateStamp, region, service);
  const signature = hmac(signingKey, stringToSign, "hex");

  const authorizationHeader =
    `${algorithm} Credential=${accessKeyId}/${credentialScope}, ` +
    `SignedHeaders=${signedHeaders}, Signature=${signature}`;

  const requestOptions = {
    hostname: host,
    method,
    path: `${canonicalUri}?${canonicalQuerystring}`,
    headers: {
      "x-amz-date": amzDate,
      Authorization: authorizationHeader,
    },
  };

  return new Promise((resolve, reject) => {
    const req = https.request(requestOptions, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

async function main() {
  try {
    const host = `monitoring.${region}.amazonaws.com`;
    const params = {
      Action: "GetMetricStatistics",
      Version: "2010-08-01",
      Namespace: metricMap[service].namespace,
      MetricName: resolvedMetric,
      StartTime: startTime.toISOString(),
      EndTime: endTime.toISOString(),
      Period: period,
      "Statistics.member.1": "Average",
    };

    const dims = metricMap[service].dimensions(resource);
    if (service === "ecs" && serviceName) {
      dims.push({ Name: "ServiceName", Value: serviceName });
    }
    dims.forEach((d, i) => {
      params[`Dimensions.member.${i + 1}.Name`] = d.Name;
      params[`Dimensions.member.${i + 1}.Value`] = d.Value;
    });

    const xml = await signedRequest({ host, region, service: "monitoring", params });
    if (debug) {
      console.log("DEBUG XML (first 500 chars):\n" + xml.slice(0, 500));
    }

    // Simple XML parse for Datapoints (Query API returns <member> entries)
    const members = [...xml.matchAll(/<member>([\s\S]*?)<\/member>/g)].map((m) => m[1]);
    if (!members.length) {
      console.log("No datapoints returned. Metric may be unavailable or not enabled.");
      console.log("Tips: check metric name, time range, or enable the metric in CloudWatch.");
      if (knownAliases.length) {
        console.log(`Available aliases for ${service}: ${knownAliases.join(", ")}`);
      }
      return;
    }

    const values = members
      .map((p) => {
        const avg = p.match(/<Average>([\d.]+)<\/Average>/);
        return avg ? Number(avg[1]) : null;
      })
      .filter((v) => v !== null);

    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((sum, v) => sum + v, 0) / values.length;

    console.log(
      `OK. Service=${service.toUpperCase()} Metric=${resolvedMetric} Resource=${resource} Region=${region} Period=${period}s Window=${hours}h`
    );
    console.log(`Summary: min=${min.toFixed(2)} max=${max.toFixed(2)} avg=${avg.toFixed(2)}`);
  } catch (err) {
    console.error("Failed to query CloudWatch:", err?.name || err);
    console.error(err?.message || err);
    if (err?.name === "AccessDenied" || /AccessDenied/i.test(err?.message || "")) {
      console.error("Hint: verify IAM permissions for CloudWatch and resource describe APIs.");
    }
    process.exit(1);
  }
}

main();
