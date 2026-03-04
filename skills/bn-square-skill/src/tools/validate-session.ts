import { getEndpointPath } from "../api/endpoints";
import {
  asRecord,
  binanceEnvelopeSchema,
  extractDataRecord,
  extractEnvelopeMessage,
  extractStringCandidate,
  isEnvelopeSuccess,
  type ValidateSessionResult,
  validateSessionResultSchema
} from "../api/types";
import type { BinanceConfig } from "../config/schema";
import { ApiError, SessionExpiredError, toSafeErrorMessage } from "../utils/errors";

export type ValidateSessionDependencies = {
  client: {
    getJson: (path: string) => Promise<unknown>;
  };
  config: BinanceConfig;
};

export const validateSession = async (dependencies: ValidateSessionDependencies): Promise<ValidateSessionResult> => {
  const endpoint = getEndpointPath(dependencies.config, "validateSession");

  try {
    const rawResponse = await dependencies.client.getJson(endpoint);
    const envelope = binanceEnvelopeSchema.parse(rawResponse);

    if (!isEnvelopeSuccess(envelope)) {
      return validateSessionResultSchema.parse({
        valid: false,
        error: extractEnvelopeMessage(envelope)
      });
    }

    const data = extractDataRecord(envelope) ?? {};
    const nestedUser = asRecord(data.user) ?? asRecord(data.profile) ?? {};

    const userId =
      extractStringCandidate(data, ["userId", "uid", "id"]) ??
      extractStringCandidate(nestedUser, ["userId", "uid", "id"]);
    const username =
      extractStringCandidate(data, ["username", "nickName", "nickname"]) ??
      extractStringCandidate(nestedUser, ["username", "nickName", "nickname"]);

    return validateSessionResultSchema.parse({
      valid: true,
      ...(userId ? { userId } : {}),
      ...(username ? { username } : {})
    });
  } catch (error) {
    if (error instanceof SessionExpiredError) {
      return validateSessionResultSchema.parse({
        valid: false,
        error: "Session expired or unauthorized"
      });
    }

    if (error instanceof ApiError && error.status === 404) {
      return validateSessionResultSchema.parse({
        valid: false,
        error: "Session validation endpoint is not configured correctly"
      });
    }

    return validateSessionResultSchema.parse({
      valid: false,
      error: toSafeErrorMessage(error, "Unable to validate session")
    });
  }
};
