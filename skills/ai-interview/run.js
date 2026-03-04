#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import process from "process";
import axios from "axios";
import FormData from "form-data";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Hardcoded Fuku.ai endpoints - these are fixed and cannot be overridden
const UPLOAD_URL = "https://hapi.fuku.ai/hr/rc/anon/file/upload";
const JOB_API_BASE = "https://hapi.fuku.ai/hr/rc/anon/job/invite/ai_interview";

function usage(msg) {
  if (msg) console.error(`\nError: ${msg}\n`);
  console.error(
    `Usage: node run.js --folder <resume_dir> --jobTitle <title> --company <company> --email <email>`,
  );
  process.exit(1);
}

const args = process.argv.slice(2);
const argMap = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i];
  const value = args[i + 1];
  if (!key?.startsWith("--")) usage(`Unexpected argument ${key}`);
  if (value === undefined) usage(`Missing value for ${key}`);
  argMap[key.slice(2)] = value;
}

const { folder, jobTitle, company, email } = argMap;
if (!folder || !jobTitle || !company || !email) {
  usage("folder, jobTitle, company, email are required");
}

const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
if (!emailRegex.test(email)) usage("Invalid email format");

const allowedExt = new Set([".pdf", ".doc", ".docx"]);
function listResumeFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = entries
    .filter((entry) => entry.isFile())
    .map((entry) => path.join(dir, entry.name))
    .filter((fullPath) => allowedExt.has(path.extname(fullPath).toLowerCase()));
  if (!files.length) {
    throw new Error(
      `No resumes found in ${dir} (accepted: ${Array.from(allowedExt).join(", ")})`,
    );
  }
  if (files.length > 100) {
    throw new Error(
      `Too many resumes (${files.length}). Limit is 100 per batch.`,
    );
  }
  return files;
}

async function uploadResume(filePath) {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));
  form.append("hour", 24 * 400);
  const response = await axios.post(UPLOAD_URL, form, {
    headers: form.getHeaders(),
    maxContentLength: Infinity,
    maxBodyLength: Infinity,
  });
  const body = response.data;
  if (body?.code !== 0 || !body?.data) {
    throw new Error(
      `Upload failed for ${path.basename(filePath)}: ${body?.desc || "unknown error"}`,
    );
  }
  return body.data;
}

async function createJob(payload) {
  const response = await axios.post(JOB_API_BASE, payload, {
    params: { uid: "1873977344885133312" },
    headers: {
      "Content-Type": "application/json",
      "X-NUMBER": "job-Z4nV8cQ1LmT7XpR2bH9sJdK6WyEaF0",
    },
  });
  const body = response.data;
  if (body?.code !== 0 || !body?.data?.id) {
    throw new Error(`Job creation failed: ${body?.desc || "unknown error"}`);
  }
  return body.data;
}

async function main() {
  console.log(`Uploading resumes from ${folder}...`);
  const resumeFiles = listResumeFiles(folder);
  const uploads = [];
  for (const filePath of resumeFiles) {
    process.stdout.write(`  - ${path.basename(filePath)} ... `);
    const url = await uploadResume(filePath);
    uploads.push({ local: filePath, remote: url });
    console.log("done");
  }

  const fileUrls = uploads.map((u) => u.remote);
  console.log("Creating interview job...");
  const jobPayload = { jobTitle, company, email, fileUrls };
  const jobData = await createJob(jobPayload);

  console.log("\n✅ AI interview created");
  console.log(`   Job ID  : ${jobData.id}`);
  console.log(`   Company : ${jobData.company}`);
  console.log(`   Title   : ${jobData.title}`);
  console.log(`   Reports : ${email}`);

  const auditDir = path.join(__dirname, "jobs");
  fs.mkdirSync(auditDir, { recursive: true });
  const timestamp = new Date().toISOString().replace(/[:]/g, "-");
  const record = {
    timestamp,
    jobId: jobData.id,
    company: jobData.company,
    title: jobData.title,
  };
  fs.writeFileSync(
    path.join(auditDir, `${timestamp}.json`),
    JSON.stringify(record, null, 2),
  );

  console.log("\nResumes included:");
  uploads.forEach((u) => {
    console.log(` - ${path.basename(u.local)}`);
  });
  console.log("\nAI interview reports will be sent directly to:", email);
}

main().catch((err) => {
  console.error("\n❌ Error:", err.message || err);
  process.exit(1);
});
