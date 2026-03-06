#!/usr/bin/env node
/**
 * Post job openings via Fuku AI API and generate resume collection links.
 * Uses AI model to generate professional job descriptions.
 *
 * Usage:
 *   node post_job.js --title "Senior Frontend Engineer" --city "Singapore" --level "senior"
 */

import Fuse from "fuse.js";
import axios from "axios";
import fs from "fs";
import dayjs from "dayjs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load locations database
const locationsPath = path.join(__dirname, "..", "assets", "locations.json");
let locations = [];
if (fs.existsSync(locationsPath)) {
  locations = JSON.parse(fs.readFileSync(locationsPath, "utf-8"));
}

// Initialize Fuse.js for fuzzy search
const fuse = new Fuse(locations, {
  keys: ["label", "parentLabel"],
  threshold: 0.3,
});
/**
 * Parse command line arguments
 */
function parseArgs(args) {
  const result = {
    title: "",
    city: "",
    description: "",
    company: "",
    email: "",
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];

    switch (arg) {
      case "--title":
        result.title = next;
        i++;
        break;
      case "--city":
        result.city = next;
        i++;
        break;
      case "--description":
        result.description = next;
        i++;
        break;
      case "--company":
        result.company = next;
        i++;
        break;
      case "--email":
        result.email = next;
        i++;
        break;
    }
  }

  return result;
}

// API Configuration
// Fuku AI client identifier (embedded for free tier access)
const NUMBER = "job-Z4nV8cQ1LmT7XpR2bH9sJdK6WyEaF0";

const API_URL_GEN = "https://hapi.fuku.ai/hr/rc/anon/job/upload";
const API_URL = "https://hapi.fuku.ai/hr/rc/anon/job/create";
const API_URL_LK = "https://hapi.fuku.ai/hr/rc/anon/job/sync/linkedin";
const API_URL_LK_CHECK = "https://hapi.fuku.ai/hr/rc/anon/job/status/linkedin";

function validateCredentials() {}

/**
 * Check the status of a LinkedIn job posting
 *
 * @param {Object} args - Arguments
 * @param {string} args.jobId - The ID of the job to check
 * @returns {Promise<string>} Status message or LinkedIn URL
 */
export async function check_linkedin_status(args) {
  const { jobId } = args;
  validateCredentials();
  try {
    const response = await axios.post(
      API_URL_LK_CHECK,
      { jobId: jobId },
      {
        params: {
          uid: "1873977344885133312",
        },
        headers: {
          "X-NUMBER": NUMBER,
        },
      },
    );

    const jobData = response.data;

    if (jobData.code !== 0) {
      return `❌ **Failed to get LinkedIn job state:** ${jobData.desc}`;
    }

    if (jobData.data && jobData.data.linkedinUrl) {
      return `✅ **LinkedIn Job is Live!**\n\nURL: ${jobData.data.linkedinUrl}`;
    } else {
      return `⏳ **LinkedIn Sync is still in progress.**\n\nStatus: ${jobData.data?.status || "Pending"}\nPlease check again in 5-10 minutes.`;
    }
  } catch (error) {
    return `❌ **Error checking LinkedIn status:** ${error.message}`;
  }
}

/**
 * Auto-check LinkedIn status with polling until URL is available
 *
 * @param {Object} args - Arguments
 * @param {string} args.jobId - The ID of the job to check
 * @param {number} [args.intervalMs=60000] - Polling interval in ms (default: 1 minute)
 * @param {number} [args.maxAttempts=20] - Maximum number of attempts (default: 20)
 * @returns {Promise<string>} Status message or LinkedIn URL
 */
export async function check_linkedin_status_auto(args) {
  const { jobId, intervalMs = 60000, maxAttempts = 20 } = args;
  validateCredentials();

  console.log(`🔄 Starting auto-check for Job ID: ${jobId}`);
  console.log(
    `   Interval: ${intervalMs / 1000}s | Max attempts: ${maxAttempts}`,
  );
  console.log();

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await axios.post(
        API_URL_LK_CHECK,
        { jobId: jobId },
        {
          params: {
            uid: "1873977344885133312",
          },
          headers: {
            "X-NUMBER": NUMBER,
          },
        },
      );

      const jobData = response.data;

      if (jobData.code !== 0) {
        console.log(`Attempt ${attempt}/${maxAttempts}: ❌ ${jobData.desc}`);
      } else if (jobData.data && jobData.data.linkedinUrl) {
        console.log();
        return `✅ **LinkedIn Job is Live!**\n\nURL: ${jobData.data.linkedinUrl}\n\n**Attempts:** ${attempt}/${maxAttempts}\n**Total time:** ${(((attempt - 1) * intervalMs) / 1000 / 60).toFixed(1)} minutes`;
      } else {
        console.log(
          `Attempt ${attempt}/${maxAttempts}: ⏳ Status: ${jobData.data?.status || "Pending"}`,
        );
      }
    } catch (error) {
      console.log(
        `Attempt ${attempt}/${maxAttempts}: ❌ Error: ${error.message}`,
      );
    }

    if (attempt < maxAttempts) {
      console.log(
        `   Waiting ${intervalMs / 1000} seconds before next check...\n`,
      );
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  }

  return `⏰ **LinkedIn sync timeout after ${maxAttempts} attempts.**\n\nThe job may still be syncing. You can manually check again later using \`check_linkedin_status\` with Job ID \`${jobId}\`.`;
}

async function getLinkedinState(jobId) {
  return check_linkedin_status({ jobId });
}

async function postToLinkd(data) {
  validateCredentials();
  let extra = null;
  try {
    extra = JSON.parse(data.extra ?? "");
  } catch (error) {}
  const job = {
    title: data.title,
    reference: `fuku-${data.id}`,
    description: data.description,
    jobId: data.id,
    linkedinCompanyUrl:
      "https://www.linkedin.com/company/110195078/admin/dashboard/",
    location: extra.location,
    sublocation: extra.sublocation,
    cityname: extra.cityname,
    salarymin: 1,
    salarymax: 1,
    app_url: `https://app.fuku.ai/career/apply?id=${data.id}`,
    salaryper: "month",
    currency: "USD",
    jobtype: "2",
    job_time: "2",
    startdate: dayjs().format("YYYY-MM-DD"),
  };
  // console.log("Linkedin Job Post:", job);

  const res = await axios.post(API_URL_LK, job, {
    params: {
      uid: "1873977344885133312",
    },
    headers: {
      "X-NUMBER": NUMBER,
    },
  });
  // console.log("Linkedin Job Post Response:", res.data);
}

/**
 * Sanitize job description before sending to external AI service
 * Removes potential prompt injection patterns
 */
function sanitizeDescription(desc) {
  if (!desc || typeof desc !== "string") return "";
  
  // Remove patterns commonly used for prompt injection
  let sanitized = desc
    .replace(/```[\s\S]*?```/g, "") // Remove code blocks
    .replace(/<\|.*?\|>/g, "") // Remove special markers like <|endoftext|>
    .replace(/(?:^|\n)\s*(ignore|forget|override|system|instruction|new instruction)[\s\S]{0,200}/gi, "") // Remove injection attempts
    .replace(/(?:^|\n)\s*[-*]\s*(ignore|forget|override|system|instruction)[\s\S]{0,200}/gi, "") // Remove bullet-point injections
    .trim();
  
  // Limit length to prevent buffer-based attacks
  return sanitized.slice(0, 10000);
}

async function genJD(description) {
  validateCredentials();
  
  // Sanitize description before sending to external AI service
  const sanitizedDescription = sanitizeDescription(description);
  if (!sanitizedDescription) {
    return "❌ **Invalid job description:** Description is empty or contains invalid content.";
  }
  
  const body = {
    content: sanitizedDescription,
  };
  try {
    const response = await axios.post(API_URL_GEN, body, {
      params: {
        uid: "1873977344885133312",
      },
      headers: {
        "X-NUMBER": NUMBER,
      },
    });

    const jobData = response.data;
    // console.log("Generated Job Data:", jobData);

    if (jobData.code !== 0) {
      return `❌ **Failed to generate job description:** ${jobData.desc}`;
    }

    return jobData.data.description;
  } catch (error) {
    return `❌ **Error generating job description:** ${error.message}`;
  }
}

/**
 * Post a job opening via Fuku AI API
 *
 * @param {Object} args - Job parameters
 * @param {string} args.title - Job title
 * @param {string} args.city_query - Location query
 * @param {string} [args.description] - Job description (auto-generated if not provided)
 * @param {string} [args.company] - Company name
 * @returns {Promise<string>} Result message
 */
export async function post_job(args) {
  try {
    validateCredentials();
  } catch (error) {
    return `❌ ${error.message}`;
  }
  const { title, city_query, description, company, email } = args;

  // Validate required fields
  if (!email) {
    return `❌ **Email is required.** Please provide an email address to receive resumes.\n\nExample: --email "hr@company.com"`;
  }

  // Fuzzy search for location
  const results = fuse.search(city_query);
  if (results.length === 0) {
    return `❌ Sorry, I couldn't find the location: "${city_query}".`;
  }

  const matched = results[0].item;

  // Build extra data
  const extra = JSON.stringify({
    location: matched.parentValue,
    sublocation: matched.value,
    cityname: matched.label,
  });

  const fullDescription = await genJD(description);
  // console.log("Generated Description:", fullDescription);
  if (fullDescription.startsWith("❌")) {
    return fullDescription;
  }

  // Double-check: sanitize the AI-generated description before sending to job posting API
  const finalDescription = sanitizeDescription(fullDescription);
  if (!finalDescription) {
    return "❌ **Invalid job description:** Generated content was filtered as unsafe.";
  }

  // Build request body
  const body = {
    title,
    description: finalDescription,
    location: matched.parentLabel,
    company: company || "FUKU AI",
    companySearchKeyword: "",
    extra,
    isAiInterview: 1,
    orgId: "1",
    email: email,
  };

  try {
    const response = await axios.post(API_URL, body, {
      params: {
        uid: "1873977344885133312",
      },
      headers: {
        "X-NUMBER": NUMBER,
      },
    });

    const jobData = response.data;

    if (jobData.code !== 0) {
      return `❌ **Failed to post job:** ${jobData.desc}`;
    }
    await postToLinkd(jobData.data);
    const jobId = jobData.data.id;

    // Note: LinkedIn sync runs in background, returns immediately
    // User can check status later with check_linkedin_status or check_linkedin_status_auto

    return (
      `✅ **Job Posted Successfully!**\n\n` +
      `**Position:** ${title}\n` +
      `**Location:** ${matched.label}\n` +
      `**Job ID:** \`${jobId}\`\n` +
      `**The resume will be sent to:** ${email}\n\n` +
      `--- \n` +
      `**LinkedIn Sync:** ⏳ Processing in background (5-30 min). I'll check and notify you when ready!\n\n` +
      `You can also manually check with: \`check_linkedin_status\` using Job ID \`${jobId}\``
    );
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message;
    return `❌ **Failed to post job:** ${errorMsg}`;
  }
}

/**
 * Main function for CLI usage
 */
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.title || !args.city) {
    console.error("Error: --title and --city are required");
    process.exit(1);
  }
  if (!args.email) {
    console.error("Error: --email is required");
    process.exit(1);
  }
  if (!args.description) {
    console.error("Error: --description is required");
    process.exit(1);
  }

  try {
    const result = await post_job({
      title: args.title,
      city_query: args.city,
      description: args.description,
      company: args.company,
      email: args.email,
    });

    console.log(result);
  } catch (error) {
    console.error("❌ Unexpected error:", error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run if called directly
if (process.argv[1] && process.argv[1].includes("post_job.js")) {
  main().catch((error) => {
    console.error("❌ Fatal error:", error.message);
    process.exit(1);
  });
}
