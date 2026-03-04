#!/usr/bin/env node

/**
 * UCloud US3 - Upload files to object storage
 * Supports uploading files and generating public URLs
 */

import { parseArgs } from "node:util";
import { existsSync, statSync, createReadStream } from "node:fs";
import { basename } from "node:path";
import { createRequire } from "node:module";
import https from "node:https";
import crypto from "node:crypto";

const require = createRequire(import.meta.url);
const ufile = require('ufile');

// Parse command line arguments
const { values } = parseArgs({
  options: {
    file: { type: "string" },
    key: { type: "string" },
    "url-only": { type: "boolean", default: false },
  },
});

const publicKey = process.env.US3_PUBLIC_KEY;
const privateKey = process.env.US3_PRIVATE_KEY;
const bucket = process.env.US3_BUCKET;

// Validate credentials
if (!publicKey || !privateKey || !bucket) {
  console.error(JSON.stringify({
    error: "missing_credentials",
    message: "US3_PUBLIC_KEY, US3_PRIVATE_KEY, and US3_BUCKET environment variables must be set. Get credentials from https://console.ucloud.cn/"
  }, null, 2));
  process.exit(1);
}

// Validate file parameter
if (!values.file) {
  console.error(JSON.stringify({
    error: "missing_file",
    message: "Please provide --file parameter with the path to upload"
  }, null, 2));
  process.exit(1);
}

if (!existsSync(values.file)) {
  console.error(JSON.stringify({
    error: "file_not_found",
    message: `File not found: ${values.file}`
  }, null, 2));
  process.exit(1);
}

/**
 * Generate UCloud signature for authentication
 */
function generateSignature(method, bucket, objectKey, contentType, contentMD5, date, privateKey) {
  const canonicalizedResource = `/${bucket}/${objectKey}`;
  const stringToSign = `${method}\n${contentMD5}\n${contentType}\n${date}\n${canonicalizedResource}`;

  const hmac = crypto.createHmac('sha1', privateKey);
  hmac.update(stringToSign);
  return hmac.digest('base64');
}

/**
 * Upload file directly using Node.js https module with timeout control
 * This is more reliable for large files than the ufile SDK
 */
async function uploadFileDirect(filepath, key) {
  console.error(`[DEBUG] Starting direct upload for: ${filepath}`);

  return new Promise((resolve, reject) => {
    const fileStats = statSync(filepath);
    const fileSize = fileStats.size;
    const objectKey = key || basename(filepath);

    console.error(`[DEBUG] File size: ${fileSize} bytes, objectKey: ${objectKey}`);

    // Extract bucket name and proxy suffix
    const bucketName = bucket.split('.')[0];
    const proxySuffix = bucket.substring(bucketName.length + 1);

    console.error(`[DEBUG] Bucket: ${bucketName}, Proxy: ${proxySuffix}`);

    const contentType = 'application/octet-stream';
    const contentMD5 = '';
    const date = new Date().toUTCString();

    // Generate authorization signature
    const signature = generateSignature('PUT', bucketName, objectKey, contentType, contentMD5, date, privateKey);
    const authorization = `UCloud ${publicKey}:${signature}`;

    console.error(`[DEBUG] Authorization generated, date: ${date}`);

    const options = {
      hostname: `${bucketName}.${proxySuffix}`,
      port: 443,
      path: `/${objectKey}`,
      method: 'PUT',
      headers: {
        'Authorization': authorization,
        'Content-Type': contentType,
        'Content-Length': fileSize,
        'Date': date,
      },
      timeout: 120000, // 120 second timeout
    };

    console.error(`[DEBUG] Creating HTTPS request to: ${options.hostname}${options.path}`);

    const req = https.request(options, (res) => {
      console.error(`[DEBUG] Got response: ${res.statusCode}`);
      let responseBody = '';

      res.on('data', (chunk) => {
        responseBody += chunk;
      });

      res.on('end', () => {
        console.error(`[DEBUG] Response complete: ${res.statusCode}`);
        if (res.statusCode === 200) {
          const publicUrl = `https://${bucket}/${objectKey}`;
          resolve({
            success: true,
            url: publicUrl,
            key: objectKey,
            bucket: bucket,
            statusCode: res.statusCode,
          });
        } else {
          reject(new Error(`Upload failed: ${res.statusCode} - ${responseBody}`));
        }
      });
    });

    req.on('error', (error) => {
      console.error(`[DEBUG] Request error: ${error.message}`);
      reject(new Error(`Network error: ${error.message}`));
    });

    req.on('timeout', () => {
      console.error(`[DEBUG] Request timeout`);
      req.destroy();
      reject(new Error('Upload timeout: request exceeded 120 seconds'));
    });

    console.error(`[DEBUG] Starting file stream`);

    // Stream the file
    const fileStream = createReadStream(filepath);
    fileStream.pipe(req);

    fileStream.on('error', (error) => {
      console.error(`[DEBUG] File stream error: ${error.message}`);
      reject(new Error(`File read error: ${error.message}`));
    });
  });
}

/**
 * Upload file to US3 using SDK (for small files) or direct HTTPS (for large files)
 */
async function uploadFile(filepath, key) {
  const fileStats = statSync(filepath);
  const fileSize = fileStats.size;
  const SIZE_THRESHOLD = 1024 * 1024; // 1MB threshold

  // Use direct HTTPS upload for files larger than 1MB
  if (fileSize > SIZE_THRESHOLD) {
    return uploadFileDirect(filepath, key);
  }

  // Use SDK for small files
  // Create timeout promise (5 minutes for large files)
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => {
      reject(new Error('Upload timeout: operation exceeded 5 minutes'));
    }, 5 * 60 * 1000);
  });

  // Create upload promise
  const uploadPromise = new Promise((resolve, reject) => {
    try {
      // Determine object key
      const objectKey = key || basename(filepath);

      // Extract bucket name from full domain
      // Format: bucket-name.region.ufileos.com -> bucket-name
      const bucketName = bucket.split('.')[0];

      // Extract proxy suffix (e.g., "cn-sh2.ufileos.com")
      const proxySuffix = bucket.substring(bucketName.length + 1);

      // Create HTTP request for PUT operation
      const httpRequest = new ufile.HttpRequest(
        'PUT',
        '/' + objectKey,
        bucketName,
        objectKey,
        filepath
      );

      // Create auth client
      const authClient = new ufile.AuthClient(httpRequest, {
        'ucloud_public_key': publicKey,
        'ucloud_private_key': privateKey,
        'proxy_suffix': proxySuffix
      });

      // Send request with error handling
      authClient.SendRequest((response) => {
        try {
          if (response.statusCode === 200) {
            // Generate public URL
            const publicUrl = `https://${bucket}/${objectKey}`;

            resolve({
              success: true,
              url: publicUrl,
              key: objectKey,
              bucket: bucket,
              statusCode: response.statusCode,
            });
          } else {
            reject(new Error(`Upload failed: ${response.statusCode} - ${JSON.stringify(response.body)}`));
          }
        } catch (error) {
          reject(error);
        }
      });
    } catch (error) {
      reject(error);
    }
  });

  // Race between upload and timeout
  return Promise.race([uploadPromise, timeoutPromise]);
}

// Main execution
(async () => {
  try {
    const result = await uploadFile(values.file, values.key);

    // Output based on --url-only flag
    if (values["url-only"]) {
      console.log(result.url);
    } else {
      console.log(JSON.stringify(result, null, 2));
    }
  } catch (error) {
    console.error(JSON.stringify({
      error: "upload_error",
      message: error.message,
      file: values.file,
    }, null, 2));
    process.exit(1);
  }
})();
