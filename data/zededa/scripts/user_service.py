#!/usr/bin/env python3
"""
ZEDEDA User / IAM Service — 67 endpoints

Covers identity and access management: users, roles, realms, auth profiles,
credentials, enterprises, sessions/tokens, login/logout flows, entitlements,
cloud policies, and enterprise reports.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import UserServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class UserService:
    """User / IAM Service."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # AUTH PROFILES
    # ======================================================================

    def query_auth_profiles(self, **kw: Any) -> Any:
        """GET /v1/authorization/profiles — Query auth profiles."""
        return self.c.get("/v1/authorization/profiles", query=_qp(kw))

    def create_auth_profile(self, body: dict) -> Any:
        """POST /v1/authorization/profiles — Create auth profile."""
        return self.c.post("/v1/authorization/profiles", body=body)

    def get_auth_profile(self, id: str) -> Any:
        """GET /v1/authorization/profiles/id/{id}"""
        return self.c.get(f"/v1/authorization/profiles/id/{id}")

    def update_auth_profile(self, id: str, body: dict) -> Any:
        """PUT /v1/authorization/profiles/id/{id}"""
        return self.c.put(f"/v1/authorization/profiles/id/{id}", body=body)

    def delete_auth_profile(self, id: str) -> Any:
        """DELETE /v1/authorization/profiles/id/{id}"""
        return self.c.delete(f"/v1/authorization/profiles/id/{id}")

    def get_auth_profile_by_name(self, name: str) -> Any:
        """GET /v1/authorization/profiles/name/{name}"""
        return self.c.get(f"/v1/authorization/profiles/name/{name}")

    # ======================================================================
    # CLOUD POLICIES
    # ======================================================================

    def query_doc_policies(self, **kw: Any) -> Any:
        """GET /v1/cloud/policies — Query document policies."""
        return self.c.get("/v1/cloud/policies", query=_qp(kw))

    def create_doc_policy(self, body: dict) -> Any:
        """POST /v1/cloud/policies — Create document policy."""
        return self.c.post("/v1/cloud/policies", body=body)

    def get_doc_policy(self, id: str) -> Any:
        """GET /v1/cloud/policies/id/{id}"""
        return self.c.get(f"/v1/cloud/policies/id/{id}")

    def delete_doc_policy(self, id: str) -> Any:
        """DELETE /v1/cloud/policies/id/{id}"""
        return self.c.delete(f"/v1/cloud/policies/id/{id}")

    def update_doc_policy_latest(self, body: dict) -> Any:
        """PUT /v1/cloud/policies/latest — Update latest document policy."""
        return self.c.put("/v1/cloud/policies/latest", body=body)

    # ======================================================================
    # CREDENTIALS
    # ======================================================================

    def create_credential(self, body: dict) -> Any:
        """POST /v1/credentials — Create credential."""
        return self.c.post("/v1/credentials", body=body)

    def update_credential(self, body: dict) -> Any:
        """PUT /v1/credentials — Update credential."""
        return self.c.put("/v1/credentials", body=body)

    def delete_credential(self, id: str) -> Any:
        """DELETE /v1/credentials/id/{id}"""
        return self.c.delete(f"/v1/credentials/id/{id}")

    def update_credential_self(self, body: dict) -> Any:
        """PUT /v1/credentials/self — Update own credential."""
        return self.c.put("/v1/credentials/self", body=body)

    # ======================================================================
    # ENTERPRISES
    # ======================================================================

    def query_enterprises(self, **kw: Any) -> Any:
        """GET /v1/enterprises — Query enterprises."""
        return self.c.get("/v1/enterprises", query=_qp(kw))

    def create_enterprise(self, body: dict) -> Any:
        """POST /v1/enterprises — Create enterprise."""
        return self.c.post("/v1/enterprises", body=body)

    def get_enterprise(self, id: str) -> Any:
        """GET /v1/enterprises/id/{id}"""
        return self.c.get(f"/v1/enterprises/id/{id}")

    def update_enterprise_by_id(self, id: str, body: dict) -> Any:
        """PUT /v1/enterprises/id/{id} (UpdateEnterprise2)"""
        return self.c.put(f"/v1/enterprises/id/{id}", body=body)

    def delete_enterprise(self, id: str) -> Any:
        """DELETE /v1/enterprises/id/{id}"""
        return self.c.delete(f"/v1/enterprises/id/{id}")

    def get_enterprise_by_name(self, name: str) -> Any:
        """GET /v1/enterprises/name/{name}"""
        return self.c.get(f"/v1/enterprises/name/{name}")

    def get_enterprise_self(self) -> Any:
        """GET /v1/enterprises/self — Get own enterprise."""
        return self.c.get("/v1/enterprises/self")

    def update_enterprise_self(self, body: dict) -> Any:
        """PUT /v1/enterprises/self — Update own enterprise."""
        return self.c.put("/v1/enterprises/self", body=body)

    # ======================================================================
    # ENTITLEMENTS
    # ======================================================================

    def get_enterprise_entitlement_data(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/entitlements"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/entitlements", query=_qp(q))

    def create_enterprise_entitlement_data(self, body: dict) -> Any:
        """PUT /v1/entitlements"""
        return self.c.put("/v1/entitlements", body=body)

    def get_allowed_enterprises_for_entitlements(self, **kw: Any) -> Any:
        """GET /v1/entitlements/allowedenterprises"""
        return self.c.get("/v1/entitlements/allowedenterprises", query=_qp(kw))

    # ======================================================================
    # LOGIN / LOGOUT
    # ======================================================================

    def login(self, body: dict) -> Any:
        """POST /v1/login — Authenticate user."""
        return self.c.post("/v1/login", body=body)

    def login_external(self, body: dict) -> Any:
        """POST /v1/login/external — External login."""
        return self.c.post("/v1/login/external", body=body)

    def login_forgot_password(self, body: dict) -> Any:
        """POST /v1/login/forgot — Forgot password flow."""
        return self.c.post("/v1/login/forgot", body=body)

    def login_mode(self, body: dict) -> Any:
        """POST /v1/login/mode — Get login mode."""
        return self.c.post("/v1/login/mode", body=body)

    def login_external_oauth2_callback(self, body: dict) -> Any:
        """POST /v1/login/oauth/callback — OAuth2 callback."""
        return self.c.post("/v1/login/oauth/callback", body=body)

    def signup_enterprise(self, body: dict) -> Any:
        """POST /v1/login/signup/enterprise — Sign up enterprise."""
        return self.c.post("/v1/login/signup/enterprise", body=body)

    def signup_user(self, body: dict) -> Any:
        """POST /v1/login/signup/user — Sign up user."""
        return self.c.post("/v1/login/signup/user", body=body)

    def logout(self, body: dict | None = None) -> Any:
        """POST /v1/logout — Logout."""
        return self.c.post("/v1/logout", body=body or {})

    # ======================================================================
    # REALMS
    # ======================================================================

    def query_realms(self, **kw: Any) -> Any:
        """GET /v1/realms — Query realms."""
        return self.c.get("/v1/realms", query=_qp(kw))

    def create_realm(self, body: dict) -> Any:
        """POST /v1/realms — Create realm."""
        return self.c.post("/v1/realms", body=body)

    def get_realm(self, id: str) -> Any:
        """GET /v1/realms/id/{id}"""
        return self.c.get(f"/v1/realms/id/{id}")

    def update_realm(self, id: str, body: dict) -> Any:
        """PUT /v1/realms/id/{id}"""
        return self.c.put(f"/v1/realms/id/{id}", body=body)

    def delete_realm(self, id: str) -> Any:
        """DELETE /v1/realms/id/{id}"""
        return self.c.delete(f"/v1/realms/id/{id}")

    def get_realm_by_name(self, name: str) -> Any:
        """GET /v1/realms/name/{name}"""
        return self.c.get(f"/v1/realms/name/{name}")

    # ======================================================================
    # REPORTS
    # ======================================================================

    def get_allowed_enterprises(self, **kw: Any) -> Any:
        """GET /v1/reports/allowedenterprises"""
        return self.c.get("/v1/reports/allowedenterprises", query=_qp(kw))

    def get_app_instance_report(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/reports/apps/instance"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/reports/apps/instance", query=_qp(q))

    def get_device_report(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/reports/device"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/reports/device", query=_qp(q))

    def get_plugin_report(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/reports/plugin"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/reports/plugin", query=_qp(q))

    def get_project_report(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/reports/project"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/reports/project", query=_qp(q))

    def get_user_report(self, *, tenantId: str | None = None) -> Any:
        """GET /v1/reports/user"""
        q = {"tenantId": tenantId}
        return self.c.get("/v1/reports/user", query=_qp(q))

    # ======================================================================
    # ROLES
    # ======================================================================

    def query_roles(self, **kw: Any) -> Any:
        """GET /v1/roles — Query roles."""
        return self.c.get("/v1/roles", query=_qp(kw))

    def create_role(self, body: dict) -> Any:
        """POST /v1/roles — Create role."""
        return self.c.post("/v1/roles", body=body)

    def get_role(self, id: str) -> Any:
        """GET /v1/roles/id/{id}"""
        return self.c.get(f"/v1/roles/id/{id}")

    def update_role(self, id: str, body: dict) -> Any:
        """PUT /v1/roles/id/{id}"""
        return self.c.put(f"/v1/roles/id/{id}", body=body)

    def delete_role(self, id: str) -> Any:
        """DELETE /v1/roles/id/{id}"""
        return self.c.delete(f"/v1/roles/id/{id}")

    def get_role_by_name(self, name: str) -> Any:
        """GET /v1/roles/name/{name}"""
        return self.c.get(f"/v1/roles/name/{name}")

    def get_role_self(self) -> Any:
        """GET /v1/roles/self — Get own role."""
        return self.c.get("/v1/roles/self")

    # ======================================================================
    # SESSIONS / TOKENS
    # ======================================================================

    def query_user_sessions(self) -> Any:
        """GET /v1/sessions — Query user sessions."""
        return self.c.get("/v1/sessions")

    def refresh_user_session(self) -> Any:
        """PUT /v1/sessions/refresh — Refresh session."""
        return self.c.put("/v1/sessions/refresh")

    def get_user_session_self(self) -> Any:
        """GET /v1/sessions/self — Get own session."""
        return self.c.get("/v1/sessions/self")

    def get_user_session_by_query_token(self, *, session_token_base64: str | None = None) -> Any:
        """GET /v1/sessions/token — Get session via query param."""
        q = {"sessionToken.base64": session_token_base64}
        return self.c.get("/v1/sessions/token", query=_qp(q))

    def create_user_session_self(self) -> Any:
        """POST /v1/sessions/token/self — Create own session token."""
        return self.c.post("/v1/sessions/token/self")

    def get_user_session(self, session_token_base64: str) -> Any:
        """GET /v1/sessions/token/{sessionToken.base64}"""
        return self.c.get(f"/v1/sessions/token/{session_token_base64}")

    # ======================================================================
    # USERS
    # ======================================================================

    def query_users(self, **kw: Any) -> Any:
        """GET /v1/users — Query users."""
        return self.c.get("/v1/users", query=_qp(kw))

    def create_user(self, body: dict) -> Any:
        """POST /v1/users — Create user."""
        return self.c.post("/v1/users", body=body)

    def get_user(self, id: str) -> Any:
        """GET /v1/users/id/{id}"""
        return self.c.get(f"/v1/users/id/{id}")

    def update_user_by_id(self, id: str, body: dict) -> Any:
        """PUT /v1/users/id/{id} (UpdateUser2)"""
        return self.c.put(f"/v1/users/id/{id}", body=body)

    def delete_user(self, id: str) -> Any:
        """DELETE /v1/users/id/{id}"""
        return self.c.delete(f"/v1/users/id/{id}")

    def get_user_by_name(self, name: str) -> Any:
        """GET /v1/users/name/{name}"""
        return self.c.get(f"/v1/users/name/{name}")

    def get_user_self(self) -> Any:
        """GET /v1/users/self — Get own user profile."""
        return self.c.get("/v1/users/self")

    def update_user_self(self, body: dict) -> Any:
        """PUT /v1/users/self — Update own user profile."""
        return self.c.put("/v1/users/self", body=body)
