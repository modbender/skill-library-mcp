// License API error codes and error class
// Why: Unified error model ensures consistent HTTP responses and client handling

export const ErrorCode = Object.freeze({
  NONCE_UNKNOWN: "NONCE_UNKNOWN",
  NONCE_REPLAY: "NONCE_REPLAY",
  EXPIRED_CHALLENGE: "EXPIRED_CHALLENGE",
  ADDRESS_MISMATCH: "ADDRESS_MISMATCH",
  INVALID_SIGNATURE: "INVALID_SIGNATURE",
  PASS_REQUIRED: "PASS_REQUIRED",
  INSUFFICIENT_BALANCE: "INSUFFICIENT_BALANCE",
  INVALID_REQUEST: "INVALID_REQUEST",
  INTERNAL_ERROR: "INTERNAL_ERROR",
});

const HTTP_STATUS = {
  [ErrorCode.NONCE_UNKNOWN]: 400,
  [ErrorCode.NONCE_REPLAY]: 409,
  [ErrorCode.EXPIRED_CHALLENGE]: 410,
  [ErrorCode.ADDRESS_MISMATCH]: 400,
  [ErrorCode.INVALID_SIGNATURE]: 401,
  [ErrorCode.PASS_REQUIRED]: 403,
  [ErrorCode.INSUFFICIENT_BALANCE]: 403,
  [ErrorCode.INVALID_REQUEST]: 400,
  [ErrorCode.INTERNAL_ERROR]: 500,
};

export class LicenseError extends Error {
  /**
   * @param {string} code - One of ErrorCode constants
   * @param {string} [message] - Human-readable detail
   */
  constructor(code, message) {
    super(message || code);
    this.code = code;
    this.httpStatus = HTTP_STATUS[code] || 500;
  }

  toJSON() {
    return { ok: false, code: this.code, message: this.message };
  }
}
