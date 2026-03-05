#!/usr/bin/env python3
"""Unified authentication provider for AuditClaw GRC integrations.

Each function tries modern auth (stored credentials) first, then falls back
to traditional env var auth for backward compatibility.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from credential_store import get_credential


def get_aws_session(db_path):
    """Get an AWS boto3 Session, using IAM Role AssumeRole if configured.

    Auth precedence:
    1. Stored IAM Role credential -> STS AssumeRole -> temporary session
    2. Stored access key credential -> Session with explicit keys
    3. Default boto3 Session (env vars, ~/.aws/credentials, instance profile)

    Returns:
        boto3.Session
    """
    import boto3

    cred = get_credential(db_path, "aws") if db_path else None

    if cred and cred.get("auth_method") == "iam_role":
        config = cred.get("config", {})
        role_arn = config.get("role_arn")
        external_id = config.get("external_id")
        if role_arn:
            sts = boto3.client("sts")
            assume_kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": "auditclaw-grc-scan",
                "DurationSeconds": 3600,
            }
            if external_id:
                assume_kwargs["ExternalId"] = external_id
            resp = sts.assume_role(**assume_kwargs)
            temp_creds = resp["Credentials"]
            return boto3.Session(
                aws_access_key_id=temp_creds["AccessKeyId"],
                aws_secret_access_key=temp_creds["SecretAccessKey"],
                aws_session_token=temp_creds["SessionToken"],
            )

    if cred and cred.get("auth_method") == "access_key":
        secret = cred.get("secret", {})
        if isinstance(secret, dict) and secret.get("access_key_id"):
            return boto3.Session(
                aws_access_key_id=secret["access_key_id"],
                aws_secret_access_key=secret["secret_access_key"],
                region_name=secret.get("region", "us-east-1"),
            )

    # Fallback: default boto3 session (env vars / ~/.aws/credentials)
    return boto3.Session()


def get_github_client(db_path):
    """Get a GitHub client, using GitHub App JWT if configured.

    Auth precedence:
    1. Stored GitHub App credential -> JWT -> installation token
    2. Stored personal token
    3. GITHUB_TOKEN env var

    Returns:
        github.Github instance
    """
    try:
        from github import Github
    except ImportError:
        return None

    cred = get_credential(db_path, "github") if db_path else None

    if cred and cred.get("auth_method") == "github_app":
        config = cred.get("config", {})
        app_id = config.get("app_id")
        installation_id = config.get("installation_id")
        private_key = cred.get("secret")

        if app_id and installation_id and private_key:
            from github import GithubIntegration
            import time
            import jwt as pyjwt

            # Generate JWT
            now = int(time.time())
            payload = {
                "iat": now - 60,
                "exp": now + (10 * 60),
                "iss": app_id,
            }
            encoded_jwt = pyjwt.encode(payload, private_key, algorithm="RS256")

            # Get installation token
            integration = GithubIntegration(app_id, private_key)
            token = integration.get_access_token(installation_id).token
            return Github(token)

    if cred and cred.get("auth_method") == "personal_token":
        secret = cred.get("secret")
        if secret:
            token = secret if isinstance(secret, str) else secret.get("token", "")
            if token:
                return Github(token)

    # Fallback: GITHUB_TOKEN env var
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return Github(token)

    return None


def get_azure_credential(db_path):
    """Get Azure credential, using certificate-based auth if configured.

    Auth precedence:
    1. Stored certificate-based Service Principal
    2. Stored client secret
    3. DefaultAzureCredential (env vars, managed identity, CLI)

    Returns:
        tuple: (credential, subscription_id) or (None, None)
    """
    cred = get_credential(db_path, "azure") if db_path else None

    if cred:
        config = cred.get("config", {})
        subscription_id = config.get("subscription_id")
        tenant_id = config.get("tenant_id")
        client_id = config.get("client_id")

        if cred.get("auth_method") == "service_principal" and cred.get("credential_path"):
            from azure.identity import CertificateCredential
            credential = CertificateCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                certificate_path=cred["credential_path"],
            )
            return credential, subscription_id

        if cred.get("auth_method") == "client_secret":
            secret = cred.get("secret")
            if isinstance(secret, dict):
                client_secret = secret.get("client_secret", "")
            else:
                client_secret = secret or ""

            if client_secret and tenant_id and client_id:
                from azure.identity import ClientSecretCredential
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret,
                )
                return credential, subscription_id

    # Fallback: DefaultAzureCredential + env var
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if subscription_id:
        from azure.identity import DefaultAzureCredential
        return DefaultAzureCredential(), subscription_id

    return None, None


def get_gcp_credentials(db_path):
    """Get GCP credentials, using SA impersonation if configured.

    Auth precedence:
    1. Stored SA impersonation -> short-lived tokens
    2. Stored service account key
    3. google.auth.default() (GOOGLE_APPLICATION_CREDENTIALS env var)

    Returns:
        tuple: (credentials, project_id) or (None, None)
    """
    cred = get_credential(db_path, "gcp") if db_path else None

    if cred:
        config = cred.get("config", {})
        project_id = config.get("project_id")

        if cred.get("auth_method") == "sa_impersonation":
            target_sa = config.get("target_service_account")
            if target_sa:
                from google.auth import default as auth_default
                from google.auth import impersonated_credentials

                source_credentials, _ = auth_default()
                target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]

                credentials = impersonated_credentials.Credentials(
                    source_credentials=source_credentials,
                    target_principal=target_sa,
                    target_scopes=target_scopes,
                    lifetime=3600,
                )
                return credentials, project_id

        if cred.get("auth_method") == "service_account" and cred.get("credential_path"):
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_file(
                cred["credential_path"],
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            return credentials, project_id

    # Fallback: google.auth.default()
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        from google.auth import default as auth_default
        credentials, detected_project = auth_default()
        return credentials, project_id or detected_project

    return None, None


def get_idp_clients(db_path):
    """Get IDP (Google Workspace + Okta) clients.

    Auth precedence:
    1. Stored credentials from credential store
    2. Environment variables

    Returns:
        dict with 'google_service' and 'okta_config' keys (either may be None)
    """
    result = {"google_service": None, "okta_config": None}

    cred = get_credential(db_path, "idp") if db_path else None

    if cred:
        config = cred.get("config", {})

        # Google Workspace
        google_config = config.get("google", {})
        sa_key_path = google_config.get("sa_key_path") or cred.get("credential_path")
        admin_email = google_config.get("admin_email")

        if sa_key_path and admin_email and os.path.exists(sa_key_path):
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]
            creds = service_account.Credentials.from_service_account_file(sa_key_path, scopes=SCOPES)
            delegated = creds.with_subject(admin_email)
            result["google_service"] = build("admin", "directory_v1", credentials=delegated)

        # Okta
        okta_config = config.get("okta", {})
        okta_org_url = okta_config.get("org_url")
        okta_token = okta_config.get("token")

        if okta_org_url and okta_token:
            result["okta_config"] = {
                "orgUrl": okta_org_url,
                "token": okta_token,
            }

    # Fallback: environment variables
    if result["google_service"] is None:
        sa_key = os.environ.get("GOOGLE_WORKSPACE_SA_KEY")
        admin_email = os.environ.get("GOOGLE_WORKSPACE_ADMIN_EMAIL")
        if sa_key and admin_email:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]
            creds = service_account.Credentials.from_service_account_file(sa_key, scopes=SCOPES)
            delegated = creds.with_subject(admin_email)
            result["google_service"] = build("admin", "directory_v1", credentials=delegated)

    if result["okta_config"] is None:
        okta_org_url = os.environ.get("OKTA_ORG_URL")
        okta_token = os.environ.get("OKTA_API_TOKEN")
        if okta_org_url and okta_token:
            result["okta_config"] = {
                "orgUrl": okta_org_url,
                "token": okta_token,
            }

    return result


def get_auth_method(db_path, provider):
    """Return the currently configured auth method for a provider.

    Returns:
        dict with auth_method, status, config summary -- or None if not configured
    """
    cred = get_credential(db_path, provider) if db_path else None
    if not cred:
        # Check if env vars are set
        env_checks = {
            "aws": lambda: bool(os.environ.get("AWS_ACCESS_KEY_ID")),
            "github": lambda: bool(os.environ.get("GITHUB_TOKEN")),
            "azure": lambda: bool(os.environ.get("AZURE_SUBSCRIPTION_ID")),
            "gcp": lambda: bool(os.environ.get("GCP_PROJECT_ID")),
            "idp": lambda: bool(os.environ.get("GOOGLE_WORKSPACE_SA_KEY") or os.environ.get("OKTA_ORG_URL")),
        }
        env_configured = env_checks.get(provider, lambda: False)()
        if env_configured:
            return {
                "auth_method": "env_vars",
                "status": "active",
                "provider": provider,
                "note": "Using environment variables (legacy method)",
            }
        return None

    return {
        "auth_method": cred["auth_method"],
        "status": cred["status"],
        "provider": cred["provider"],
        "created_at": cred.get("created_at"),
        "last_used": cred.get("last_used"),
        "expires_at": cred.get("expires_at"),
    }
