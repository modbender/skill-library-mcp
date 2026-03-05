"""War/Den ClawHub Packaging Tests -- validate clawhub.json and SKILL.md."""

import json
import os
from pathlib import Path

import pytest


class TestClawHubJson:
    @pytest.fixture
    def clawhub(self):
        path = Path(__file__).resolve().parent.parent / "clawhub.json"
        with open(path) as f:
            return json.load(f)

    def test_name_is_warden_governance(self, clawhub):
        assert clawhub["name"] == "warden-governance"

    def test_version_is_1_0_0(self, clawhub):
        assert clawhub["version"] == "1.0.0"

    def test_author_is_an2b(self, clawhub):
        assert clawhub["author"] == "AN2B Technologies"

    def test_license_is_mit(self, clawhub):
        assert clawhub["license"] == "MIT"

    def test_has_three_hooks(self, clawhub):
        assert "before_action" in clawhub["hooks"]
        assert "after_action" in clawhub["hooks"]
        assert "on_error" in clawhub["hooks"]

    def test_has_sentinel_config(self, clawhub):
        assert "SENTINEL_API_KEY" in clawhub["config"]

    def test_has_engramport_config(self, clawhub):
        assert "ENGRAMPORT_API_KEY" in clawhub["config"]

    def test_has_clawhub_registry(self, clawhub):
        ch = clawhub["clawhub"]
        assert ch["registry"] == "clawhub.com"
        assert ch["package"] == "an2b/warden-governance"
        assert ch["category"] == "governance"
        assert ch["install_command"] == "openclaw skill install an2b/warden-governance"
        assert ch["verified"] is True

    def test_has_community_section(self, clawhub):
        assert clawhub["community"]["zero_dependencies"] is True

    def test_has_enterprise_section(self, clawhub):
        assert "sentinel_os" in clawhub["enterprise"]
        assert "engramport" in clawhub["enterprise"]

    def test_sentinel_os_endpoints(self, clawhub):
        endpoints = clawhub["enterprise"]["sentinel_os"]["endpoints"]
        assert "/api/v1/check" in endpoints
        assert "/api/v1/ingest" in endpoints

    def test_engramport_endpoints(self, clawhub):
        endpoints = clawhub["enterprise"]["engramport"]["endpoints"]
        assert "/remember" in endpoints
        assert "/recall" in endpoints
        assert "/reflect" in endpoints


class TestSkillMd:
    @pytest.fixture
    def skill_md(self):
        path = Path(__file__).resolve().parent.parent / "SKILL.md"
        with open(path) as f:
            return f.read()

    def test_skill_md_exists(self, skill_md):
        assert len(skill_md) > 100

    def test_mentions_meta_inbox(self, skill_md):
        assert "Meta" in skill_md
        assert "inbox" in skill_md.lower() or "email" in skill_md.lower()

    def test_mentions_community_mode(self, skill_md):
        assert "community" in skill_md.lower() or "Community" in skill_md

    def test_mentions_enterprise(self, skill_md):
        assert "enterprise" in skill_md.lower() or "Enterprise" in skill_md

    def test_mentions_sentinel_os(self, skill_md):
        assert "getsentinelos.com" in skill_md

    def test_mentions_engramport(self, skill_md):
        assert "engramport" in skill_md.lower() or "EngramPort" in skill_md

    def test_mentions_install_command(self, skill_md):
        assert "openclaw skill install" in skill_md


class TestReadme:
    @pytest.fixture
    def readme(self):
        path = Path(__file__).resolve().parent.parent / "README.md"
        with open(path) as f:
            return f.read()

    def test_readme_exists(self, readme):
        assert len(readme) > 100

    def test_mentions_meta_incident(self, readme):
        assert "200 emails" in readme

    def test_mentions_test_proof(self, readme):
        assert "blocked_count == 200" in readme

    def test_mentions_community_zero_deps(self, readme):
        assert "zero" in readme.lower() and "depend" in readme.lower()


class TestPolicyFile:
    @pytest.fixture
    def policy_yaml(self):
        path = Path(__file__).resolve().parent.parent / "policies" / "openclaw_default.yaml"
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)

    def test_policy_file_has_policies(self, policy_yaml):
        assert "policies" in policy_yaml
        assert len(policy_yaml["policies"]) >= 6

    def test_email_delete_policy_exists(self, policy_yaml):
        names = [p["name"] for p in policy_yaml["policies"]]
        assert "protect-email-delete" in names

    def test_shell_execute_policy_exists(self, policy_yaml):
        names = [p["name"] for p in policy_yaml["policies"]]
        assert "block-shell-execute-prod" in names

    def test_payment_policy_exists(self, policy_yaml):
        names = [p["name"] for p in policy_yaml["policies"]]
        assert "review-payments" in names

    def test_all_policies_have_required_fields(self, policy_yaml):
        required = {"name", "match", "decision", "mode", "priority", "active"}
        for policy in policy_yaml["policies"]:
            missing = required - set(policy.keys())
            assert not missing, (
                f"Policy '{policy.get('name')}' missing: {missing}"
            )
