// HTTP server for License API
// Why: Minimal Node built-in HTTP — zero external deps for the transport layer
import http from "node:http";
import { LicenseService } from "./licenseService.js";
import { LicenseError, ErrorCode } from "./errors.js";

const PORT = parseInt(process.env.LICENSE_PORT || "3100", 10);
const JWT_SECRET = process.env.JWT_SECRET || "dev-secret-CHANGE-ME";

const service = new LicenseService({ jwtSecret: JWT_SECRET });

/**
 * Read JSON body from request. Rejects if body is too large or malformed.
 * @param {http.IncomingMessage} req
 * @param {number} [maxBytes=4096]
 * @returns {Promise<object>}
 */
function readBody(req, maxBytes = 4096) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        let size = 0;
        req.on("data", (chunk) => {
            size += chunk.length;
            if (size > maxBytes) {
                req.destroy();
                reject(new LicenseError(ErrorCode.INVALID_REQUEST, "Body too large"));
            }
            chunks.push(chunk);
        });
        req.on("end", () => {
            try {
                resolve(JSON.parse(Buffer.concat(chunks).toString()));
            } catch {
                reject(new LicenseError(ErrorCode.INVALID_REQUEST, "Invalid JSON"));
            }
        });
        req.on("error", reject);
    });
}

/** Send JSON response */
function json(res, status, data) {
    const body = JSON.stringify(data);
    res.writeHead(status, {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
    });
    res.end(body);
}

/** Route handler */
async function handleRequest(req, res) {
    // CORS preflight
    if (req.method === "OPTIONS") {
        res.writeHead(204, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        });
        return res.end();
    }

    res.setHeader("Access-Control-Allow-Origin", "*");

    try {
        // POST /license/challenge
        if (req.method === "POST" && req.url === "/license/challenge") {
            const { address } = await readBody(req);
            if (!address) {
                return json(res, 400, { ok: false, code: ErrorCode.INVALID_REQUEST, message: "address required" });
            }
            const result = service.issueChallenge(address);
            return json(res, 200, { ok: true, ...result });
        }

        // POST /license/verify
        if (req.method === "POST" && req.url === "/license/verify") {
            const { address, nonce, signature, hasPass } = await readBody(req);
            const result = await service.verify({ address, nonce, signature, hasPass });
            const status = result.ok ? 200 : (result.code === ErrorCode.INVALID_SIGNATURE ? 401 : 400);
            return json(res, status, result);
        }

        // GET /health
        if (req.method === "GET" && req.url === "/health") {
            return json(res, 200, { ok: true, service: "license-api", version: "1.0.0" });
        }

        // 404
        json(res, 404, { ok: false, code: "NOT_FOUND" });
    } catch (err) {
        if (err instanceof LicenseError) {
            return json(res, err.httpStatus, err.toJSON());
        }
        console.error("[license-api] Internal error:", err);
        json(res, 500, { ok: false, code: ErrorCode.INTERNAL_ERROR });
    }
}

const server = http.createServer(handleRequest);

// Only listen if run directly (not imported for testing)
if (process.argv[1] && process.argv[1].endsWith("server.js")) {
    server.listen(PORT, () => {
        console.log(`🍈 License API listening on :${PORT}`);
    });
}

export { server, service };
