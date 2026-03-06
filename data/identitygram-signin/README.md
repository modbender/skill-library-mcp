# IdentityGram Signin Skill

Authenticate users with IdentityGram by signing in through the authentication endpoint.

## Overview

This is an OpenClaw skill that authenticates users with IdentityGram by sending credentials to the `/auth/signin` endpoint.

## Usage

This skill is used through OpenClaw's skill system. It requires:
- `email`: User's email address
- `password`: User's password

## Response

The skill returns a JSON response that may include:
- Authentication tokens (`token`, `accessToken`, `refreshToken`)
- User information (`user`)
- Success status (`success`)
- Status messages (`message`)

## How It Works

The skill sends a POST request to `https://gateway-v2.identitygram.co.uk/auth/signin` with email and password in the request body.

## Troubleshooting

**Authentication failed:**
- Verify email and password are correct
- Ensure the IdentityGram endpoint is accessible

**Connection errors:**
- Verify the endpoint URL is correct
- Check network connectivity
- Ensure the IdentityGram service is running
