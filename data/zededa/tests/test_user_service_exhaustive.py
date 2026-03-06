#!/usr/bin/env python3
"""Exhaustive unit tests for every method in UserService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.user_service import UserService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestUserService(unittest.TestCase):
    """One test per method in UserService (67 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = UserService(self.mc)

    def test_create_auth_profile(self):
        """create_auth_profile -> POST /v1/authorization/profiles"""
        self.svc.create_auth_profile(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/authorization/profiles", args[0][0])

    def test_create_credential(self):
        """create_credential -> POST /v1/credentials"""
        self.svc.create_credential(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/credentials", args[0][0])

    def test_create_doc_policy(self):
        """create_doc_policy -> POST /v1/cloud/policies"""
        self.svc.create_doc_policy(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cloud/policies", args[0][0])

    def test_create_enterprise(self):
        """create_enterprise -> POST /v1/enterprises"""
        self.svc.create_enterprise(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/enterprises", args[0][0])

    def test_create_enterprise_entitlement_data(self):
        """create_enterprise_entitlement_data -> PUT /v1/entitlements"""
        self.svc.create_enterprise_entitlement_data(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/entitlements", args[0][0])

    def test_create_realm(self):
        """create_realm -> POST /v1/realms"""
        self.svc.create_realm(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/realms", args[0][0])

    def test_create_role(self):
        """create_role -> POST /v1/roles"""
        self.svc.create_role(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/roles", args[0][0])

    def test_create_user(self):
        """create_user -> POST /v1/users"""
        self.svc.create_user(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/users", args[0][0])

    def test_create_user_session_self(self):
        """create_user_session_self -> POST /v1/sessions/token/self"""
        self.svc.create_user_session_self()
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/sessions/token/self", args[0][0])

    def test_delete_auth_profile(self):
        """delete_auth_profile -> DELETE /v1/authorization/profiles/id/{id}"""
        self.svc.delete_auth_profile(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/authorization/profiles/id/test-id", args[0][0])

    def test_delete_credential(self):
        """delete_credential -> DELETE /v1/credentials/id/{id}"""
        self.svc.delete_credential(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/credentials/id/test-id", args[0][0])

    def test_delete_doc_policy(self):
        """delete_doc_policy -> DELETE /v1/cloud/policies/id/{id}"""
        self.svc.delete_doc_policy(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cloud/policies/id/test-id", args[0][0])

    def test_delete_enterprise(self):
        """delete_enterprise -> DELETE /v1/enterprises/id/{id}"""
        self.svc.delete_enterprise(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/enterprises/id/test-id", args[0][0])

    def test_delete_realm(self):
        """delete_realm -> DELETE /v1/realms/id/{id}"""
        self.svc.delete_realm(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/realms/id/test-id", args[0][0])

    def test_delete_role(self):
        """delete_role -> DELETE /v1/roles/id/{id}"""
        self.svc.delete_role(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/roles/id/test-id", args[0][0])

    def test_delete_user(self):
        """delete_user -> DELETE /v1/users/id/{id}"""
        self.svc.delete_user(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/users/id/test-id", args[0][0])

    def test_get_allowed_enterprises(self):
        """get_allowed_enterprises -> GET /v1/reports/allowedenterprises"""
        self.svc.get_allowed_enterprises()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/allowedenterprises", args[0][0])

    def test_get_allowed_enterprises_for_entitlements(self):
        """get_allowed_enterprises_for_entitlements -> GET /v1/entitlements/allowedenterprises"""
        self.svc.get_allowed_enterprises_for_entitlements()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/entitlements/allowedenterprises", args[0][0])

    def test_get_app_instance_report(self):
        """get_app_instance_report -> GET /v1/reports/apps/instance"""
        self.svc.get_app_instance_report(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/apps/instance", args[0][0])

    def test_get_auth_profile(self):
        """get_auth_profile -> GET /v1/authorization/profiles/id/{id}"""
        self.svc.get_auth_profile(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/authorization/profiles/id/test-id", args[0][0])

    def test_get_auth_profile_by_name(self):
        """get_auth_profile_by_name -> GET /v1/authorization/profiles/name/{name}"""
        self.svc.get_auth_profile_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/authorization/profiles/name/test-name", args[0][0])

    def test_get_device_report(self):
        """get_device_report -> GET /v1/reports/device"""
        self.svc.get_device_report(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/device", args[0][0])

    def test_get_doc_policy(self):
        """get_doc_policy -> GET /v1/cloud/policies/id/{id}"""
        self.svc.get_doc_policy(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cloud/policies/id/test-id", args[0][0])

    def test_get_enterprise(self):
        """get_enterprise -> GET /v1/enterprises/id/{id}"""
        self.svc.get_enterprise(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/enterprises/id/test-id", args[0][0])

    def test_get_enterprise_by_name(self):
        """get_enterprise_by_name -> GET /v1/enterprises/name/{name}"""
        self.svc.get_enterprise_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/enterprises/name/test-name", args[0][0])

    def test_get_enterprise_entitlement_data(self):
        """get_enterprise_entitlement_data -> GET /v1/entitlements"""
        self.svc.get_enterprise_entitlement_data(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/entitlements", args[0][0])

    def test_get_enterprise_self(self):
        """get_enterprise_self -> GET /v1/enterprises/self"""
        self.svc.get_enterprise_self()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/enterprises/self", args[0][0])

    def test_get_plugin_report(self):
        """get_plugin_report -> GET /v1/reports/plugin"""
        self.svc.get_plugin_report(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/plugin", args[0][0])

    def test_get_project_report(self):
        """get_project_report -> GET /v1/reports/project"""
        self.svc.get_project_report(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/project", args[0][0])

    def test_get_realm(self):
        """get_realm -> GET /v1/realms/id/{id}"""
        self.svc.get_realm(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/realms/id/test-id", args[0][0])

    def test_get_realm_by_name(self):
        """get_realm_by_name -> GET /v1/realms/name/{name}"""
        self.svc.get_realm_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/realms/name/test-name", args[0][0])

    def test_get_role(self):
        """get_role -> GET /v1/roles/id/{id}"""
        self.svc.get_role(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/roles/id/test-id", args[0][0])

    def test_get_role_by_name(self):
        """get_role_by_name -> GET /v1/roles/name/{name}"""
        self.svc.get_role_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/roles/name/test-name", args[0][0])

    def test_get_role_self(self):
        """get_role_self -> GET /v1/roles/self"""
        self.svc.get_role_self()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/roles/self", args[0][0])

    def test_get_user(self):
        """get_user -> GET /v1/users/id/{id}"""
        self.svc.get_user(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/users/id/test-id", args[0][0])

    def test_get_user_by_name(self):
        """get_user_by_name -> GET /v1/users/name/{name}"""
        self.svc.get_user_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/users/name/test-name", args[0][0])

    def test_get_user_report(self):
        """get_user_report -> GET /v1/reports/user"""
        self.svc.get_user_report(tenantId="test-tenantId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/reports/user", args[0][0])

    def test_get_user_self(self):
        """get_user_self -> GET /v1/users/self"""
        self.svc.get_user_self()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/users/self", args[0][0])

    def test_get_user_session(self):
        """get_user_session -> GET /v1/sessions/token/{session_token_base64}"""
        self.svc.get_user_session(session_token_base64="test-session_token_base64")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sessions/token/test-session_token_base64", args[0][0])

    def test_get_user_session_by_query_token(self):
        """get_user_session_by_query_token -> GET /v1/sessions/token"""
        self.svc.get_user_session_by_query_token(session_token_base64="test-session_token_base64")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sessions/token", args[0][0])

    def test_get_user_session_self(self):
        """get_user_session_self -> GET /v1/sessions/self"""
        self.svc.get_user_session_self()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sessions/self", args[0][0])

    def test_login(self):
        """login -> POST /v1/login"""
        self.svc.login(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login", args[0][0])

    def test_login_external(self):
        """login_external -> POST /v1/login/external"""
        self.svc.login_external(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/external", args[0][0])

    def test_login_external_oauth2_callback(self):
        """login_external_oauth2_callback -> POST /v1/login/oauth/callback"""
        self.svc.login_external_oauth2_callback(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/oauth/callback", args[0][0])

    def test_login_forgot_password(self):
        """login_forgot_password -> POST /v1/login/forgot"""
        self.svc.login_forgot_password(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/forgot", args[0][0])

    def test_login_mode(self):
        """login_mode -> POST /v1/login/mode"""
        self.svc.login_mode(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/mode", args[0][0])

    def test_logout(self):
        """logout -> POST /v1/logout"""
        self.svc.logout(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/logout", args[0][0])

    def test_query_auth_profiles(self):
        """query_auth_profiles -> GET /v1/authorization/profiles"""
        self.svc.query_auth_profiles()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/authorization/profiles", args[0][0])

    def test_query_doc_policies(self):
        """query_doc_policies -> GET /v1/cloud/policies"""
        self.svc.query_doc_policies()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cloud/policies", args[0][0])

    def test_query_enterprises(self):
        """query_enterprises -> GET /v1/enterprises"""
        self.svc.query_enterprises()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/enterprises", args[0][0])

    def test_query_realms(self):
        """query_realms -> GET /v1/realms"""
        self.svc.query_realms()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/realms", args[0][0])

    def test_query_roles(self):
        """query_roles -> GET /v1/roles"""
        self.svc.query_roles()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/roles", args[0][0])

    def test_query_user_sessions(self):
        """query_user_sessions -> GET /v1/sessions"""
        self.svc.query_user_sessions()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sessions", args[0][0])

    def test_query_users(self):
        """query_users -> GET /v1/users"""
        self.svc.query_users()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/users", args[0][0])

    def test_refresh_user_session(self):
        """refresh_user_session -> PUT /v1/sessions/refresh"""
        self.svc.refresh_user_session()
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/sessions/refresh", args[0][0])

    def test_signup_enterprise(self):
        """signup_enterprise -> POST /v1/login/signup/enterprise"""
        self.svc.signup_enterprise(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/signup/enterprise", args[0][0])

    def test_signup_user(self):
        """signup_user -> POST /v1/login/signup/user"""
        self.svc.signup_user(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/login/signup/user", args[0][0])

    def test_update_auth_profile(self):
        """update_auth_profile -> PUT /v1/authorization/profiles/id/{id}"""
        self.svc.update_auth_profile(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/authorization/profiles/id/test-id", args[0][0])

    def test_update_credential(self):
        """update_credential -> PUT /v1/credentials"""
        self.svc.update_credential(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/credentials", args[0][0])

    def test_update_credential_self(self):
        """update_credential_self -> PUT /v1/credentials/self"""
        self.svc.update_credential_self(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/credentials/self", args[0][0])

    def test_update_doc_policy_latest(self):
        """update_doc_policy_latest -> PUT /v1/cloud/policies/latest"""
        self.svc.update_doc_policy_latest(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cloud/policies/latest", args[0][0])

    def test_update_enterprise_by_id(self):
        """update_enterprise_by_id -> PUT /v1/enterprises/id/{id}"""
        self.svc.update_enterprise_by_id(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/enterprises/id/test-id", args[0][0])

    def test_update_enterprise_self(self):
        """update_enterprise_self -> PUT /v1/enterprises/self"""
        self.svc.update_enterprise_self(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/enterprises/self", args[0][0])

    def test_update_realm(self):
        """update_realm -> PUT /v1/realms/id/{id}"""
        self.svc.update_realm(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/realms/id/test-id", args[0][0])

    def test_update_role(self):
        """update_role -> PUT /v1/roles/id/{id}"""
        self.svc.update_role(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/roles/id/test-id", args[0][0])

    def test_update_user_by_id(self):
        """update_user_by_id -> PUT /v1/users/id/{id}"""
        self.svc.update_user_by_id(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/users/id/test-id", args[0][0])

    def test_update_user_self(self):
        """update_user_self -> PUT /v1/users/self"""
        self.svc.update_user_self(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/users/self", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 67)


if __name__ == "__main__":
    unittest.main()
