import { ContractValidationError } from "../../src/common/contract-validation.js";
import {
  assertValidTokenRequestPayload,
  buildAuthorizationUrl,
  classifyAuthError,
  parseAuthorizationCallback,
  parseTokenResponse,
  toTokenRequestFormData,
} from "../../src/auth/oauth2-contract.js";
import { TickTickOAuth2Client } from "../../src/auth/ticktick-oauth2-client.js";
import { describe, expect, it, vi } from "vitest";

describe("auth module", () => {
  it(
    "exchanges an OAuth authorization code for access credentials",
    () => {
      const authorizationUrl = buildAuthorizationUrl("https://auth.ticktick.com/oauth/authorize", {
        clientId: "client-123",
        redirectUri: "https://app.example.com/callback",
        state: "state-token",
        scope: "tasks:read tasks:write",
        codeChallenge: "pkce-challenge",
      });

      const params = new URL(authorizationUrl).searchParams;
      expect(params.get("client_id")).toBe("client-123");
      expect(params.get("redirect_uri")).toBe("https://app.example.com/callback");
      expect(params.get("response_type")).toBe("code");
      expect(params.get("state")).toBe("state-token");
      expect(params.get("scope")).toBe("tasks:read tasks:write");
      expect(params.get("code_challenge")).toBe("pkce-challenge");
      expect(params.get("code_challenge_method")).toBe("S256");

      const request = assertValidTokenRequestPayload({
        grantType: "authorization_code",
        clientId: "client-123",
        clientSecret: "secret-xyz",
        code: "auth-code",
        redirectUri: "https://app.example.com/callback",
        codeVerifier: "pkce-verifier",
      });

      expect(request).toEqual({
        grantType: "authorization_code",
        clientId: "client-123",
        clientSecret: "secret-xyz",
        code: "auth-code",
        redirectUri: "https://app.example.com/callback",
        codeVerifier: "pkce-verifier",
      });

      const form = toTokenRequestFormData(request);
      expect(form.get("grant_type")).toBe("authorization_code");
      expect(form.get("client_id")).toBe("client-123");
      expect(form.get("client_secret")).toBe("secret-xyz");
      expect(form.get("code")).toBe("auth-code");
      expect(form.get("redirect_uri")).toBe("https://app.example.com/callback");
      expect(form.get("code_verifier")).toBe("pkce-verifier");

      const token = parseTokenResponse({
        access_token: "access-token",
        token_type: "Bearer",
        refresh_token: "refresh-token",
        scope: "tasks:write",
        expires_in: "3600",
      });

      expect(token).toEqual({
        accessToken: "access-token",
        tokenType: "Bearer",
        refreshToken: "refresh-token",
        scope: "tasks:write",
        expiresIn: 3600,
      });
    },
  );

  it(
    "refreshes expired access credentials with refresh token",
    () => {
      const request = assertValidTokenRequestPayload({
        grantType: "refresh_token",
        refreshToken: "refresh-token",
        clientId: "client-123",
        clientSecret: "secret-xyz",
      });

      expect(request).toEqual({
        grantType: "refresh_token",
        refreshToken: "refresh-token",
        clientId: "client-123",
        clientSecret: "secret-xyz",
      });

      const form = toTokenRequestFormData(request);
      expect(form.get("grant_type")).toBe("refresh_token");
      expect(form.get("refresh_token")).toBe("refresh-token");
      expect(form.get("client_id")).toBe("client-123");
      expect(form.get("client_secret")).toBe("secret-xyz");

      const refreshedToken = parseTokenResponse({
        accessToken: "new-access-token",
        tokenType: "Bearer",
        refreshToken: "new-refresh-token",
        expiresIn: 120,
      });

      expect(refreshedToken).toEqual({
        accessToken: "new-access-token",
        tokenType: "Bearer",
        refreshToken: "new-refresh-token",
        expiresIn: 120,
      });

      expect(() =>
        parseTokenResponse({
          access_token: "token",
          token_type: "Bearer",
          expires_in: -1,
        }),
      ).toThrow(ContractValidationError);
    },
  );

  it(
    "maps authentication failures to typed domain errors",
    () => {
      const callbackSuccess = parseAuthorizationCallback({
        code: "auth-code",
        state: "csrf-state",
      });
      expect(callbackSuccess).toEqual({
        ok: true,
        value: {
          code: "auth-code",
          state: "csrf-state",
        },
      });

      const callbackFailure = parseAuthorizationCallback({
        error: "invalid_grant",
        error_description: "Authorization code expired",
        state: "csrf-state",
      });
      expect(callbackFailure).toEqual({
        ok: false,
        value: {
          error: "invalid_grant",
          errorDescription: "Authorization code expired",
          state: "csrf-state",
        },
      });

      expect(() => parseAuthorizationCallback({})).toThrow(ContractValidationError);
      expect(() => parseAuthorizationCallback({ code: "x", error: "invalid_request" })).toThrow(ContractValidationError);

      const oauthError = classifyAuthError({
        error: "invalid_grant",
        error_description: "Code has expired",
      });
      expect(oauthError).toEqual({
        code: "invalid_grant",
        message: "Code has expired",
        retriable: false,
        cause: {
          error: "invalid_grant",
          error_description: "Code has expired",
        },
      });

      const timeoutError = classifyAuthError(new Error("Request timeout after 15s"));
      expect(timeoutError.code).toBe("timeout");
      expect(timeoutError.retriable).toBe(true);

      const networkError = classifyAuthError(new Error("socket hang up"));
      expect(networkError.code).toBe("network_error");
      expect(networkError.retriable).toBe(true);

      const unknownOAuthError = classifyAuthError({ error: "totally_unknown_error" });
      expect(unknownOAuthError.code).toBe("unknown");
      expect(unknownOAuthError.retriable).toBe(true);

      const unknownError = classifyAuthError("unexpected");
      expect(unknownError).toEqual({
        code: "unknown",
        message: "Unknown OAuth2 auth error",
        retriable: false,
        cause: "unexpected",
      });
    },
  );
});

describe("ticktick oauth2 client", () => {
  it("exchanges authorization code with token endpoint", async () => {
    const fetchMock = vi.fn(async (_url: string, init: { body: string }) => {
      expect(init.body).toContain("grant_type=authorization_code");
      expect(init.body).toContain("code=code-123");

      return {
        ok: true,
        status: 200,
        headers: {
          get(name: string) {
            return name.toLowerCase() === "content-type" ? "application/json" : null;
          },
        },
        async json() {
          return {
            access_token: "access-token",
            token_type: "Bearer",
            refresh_token: "refresh-token",
            expires_in: 3600,
          };
        },
        async text() {
          return "";
        },
      };
    });

    const client = new TickTickOAuth2Client({
      tokenUrl: "https://ticktick.com/oauth/token",
      clientId: "client-123",
      clientSecret: "secret-xyz",
      fetchImplementation: fetchMock,
    });

    await expect(
      client.exchangeAuthorizationCode({
        code: "code-123",
        redirectUri: "https://app.example.com/callback",
      })
    ).resolves.toMatchObject({
      accessToken: "access-token",
      refreshToken: "refresh-token",
    });
  });

  it("maps oauth error responses to TickTickOAuth2Error", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: false,
      status: 400,
      headers: {
        get(name: string) {
          return name.toLowerCase() === "content-type" ? "application/json" : null;
        },
      },
      async json() {
        return {
          error: "invalid_grant",
          error_description: "Code expired",
        };
      },
      async text() {
        return "";
      },
    }));

    const client = new TickTickOAuth2Client({
      tokenUrl: "https://ticktick.com/oauth/token",
      clientId: "client-123",
      clientSecret: "secret-xyz",
      fetchImplementation: fetchMock,
    });

    await expect(client.refreshAccessToken("refresh-token")).rejects.toMatchObject({
      flowError: {
        code: "invalid_grant",
        retriable: false,
      },
      status: 400,
    });
  });
});
