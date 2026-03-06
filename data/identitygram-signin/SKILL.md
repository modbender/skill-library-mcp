---
name: identitygram-signin
description: Sign in to IdentityGram by calling the /auth/signin endpoint.
---

# IdentityGram Signin

Sign in to IdentityGram using the authentication endpoint.

This skill authenticates a user by sending credentials to `https://gateway-v2.identitygram.co.uk/auth/signin`.

## Usage

Use this skill when you need to authenticate a user with IdentityGram credentials.

## Configuration

The skill expects the following parameters:
- `email`: User's email address
- `password`: User's password

These can be provided through OpenClaw's skill invocation system.

## Response

The skill returns a JSON response with:
- `raw`: Full response from IdentityGram API
- `success`: Boolean indicating if authentication was successful (if available)
- `token`: Authentication token (if available)
- `accessToken`: Access token (if available)
- `refreshToken`: Refresh token (if available)
- `user`: User information (if available)
- `message`: Status message (if available)

## How It Works

1. Sends a POST request to `https://gateway-v2.identitygram.co.uk/auth/signin`
2. Includes email and password in the request body as JSON
3. Returns the authentication response with tokens and user information

## Troubleshooting

**Authentication failed:**
- Verify email and password are correct
- Ensure the IdentityGram endpoint is accessible

**Connection errors:**
- Verify the endpoint URL is correct
- Check network connectivity
- Ensure the IdentityGram service is running
