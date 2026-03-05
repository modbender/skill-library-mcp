const crypto = require("crypto");
const jwt = require("jsonwebtoken");
const { v4: uuidv4 } = require("uuid");
const { loadConfig } = require("../config");
const { UpbitError } = require("./errors");

/**
 * Upbit JWT auth reference:
 * https://docs.upbit.com/kr/reference/auth
 */
function createJwt({ queryString = "" } = {}) {
  const cfg = loadConfig();
  const accessKey = cfg?.upbit?.accessKey;
  const secretKey = cfg?.upbit?.secretKey;

  if (!accessKey || !secretKey) {
    throw new UpbitError("Missing upbit.accessKey / upbit.secretKey in config");
  }

  const payload = {
    access_key: accessKey,
    nonce: uuidv4()
  };

  if (queryString) {
    const queryHash = crypto.createHash("sha512").update(queryString, "utf8").digest("hex");
    payload.query_hash = queryHash;
    payload.query_hash_alg = "SHA512";
  }

  return jwt.sign(payload, secretKey, { algorithm: "HS512" });
}

module.exports = { createJwt };

