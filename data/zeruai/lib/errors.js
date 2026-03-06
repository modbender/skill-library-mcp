/** Stable error codes for agent runtimes */
export const ErrorCode = {
    RPC_ERROR: "RPC_ERROR",
    API_ERROR: "API_ERROR",
    VALIDATION_ERROR: "VALIDATION_ERROR",
};
export class ZeruError extends Error {
    code;
    details;
    constructor(code, message, details) {
        super(message);
        this.code = code;
        this.details = details;
        this.name = "ZeruError";
        Object.setPrototypeOf(this, ZeruError.prototype);
    }
}
export function rpcError(message, details) {
    return new ZeruError(ErrorCode.RPC_ERROR, message, details);
}
export function apiError(message, status, body) {
    return new ZeruError(ErrorCode.API_ERROR, message, { status, body });
}
export function validationError(message, fields) {
    return new ZeruError(ErrorCode.VALIDATION_ERROR, message, { fields });
}
