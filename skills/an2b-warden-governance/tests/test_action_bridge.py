"""War/Den Action Bridge Tests -- all 15 OpenClaw action types must be mapped."""

import pytest

from warden_governance.action_bridge import (
    Action,
    ActionBridge,
    ActionType,
    Decision,
    HIGH_RISK_ACTIONS,
    OPENCLAW_TO_WARDEN,
)


class TestOpenClawToWardenMapping:
    def test_all_15_openclaw_types_mapped(self):
        """All 15 OpenClaw action types must have a mapping."""
        expected_types = [
            "email.send", "email.delete", "email.read",
            "file.write", "file.delete", "file.read",
            "browser.navigate", "browser.click",
            "shell.execute",
            "api.call",
            "calendar.create", "calendar.delete",
            "message.send",
            "code.execute",
            "payment.create",
        ]
        assert len(expected_types) == 15
        for oc_type in expected_types:
            assert oc_type in OPENCLAW_TO_WARDEN, f"Missing mapping for {oc_type}"

    def test_email_delete_maps_to_data_write(self):
        assert OPENCLAW_TO_WARDEN["email.delete"] == ActionType.DATA_WRITE

    def test_shell_execute_maps_to_code_execute(self):
        assert OPENCLAW_TO_WARDEN["shell.execute"] == ActionType.CODE_EXECUTE

    def test_payment_create_maps_to_api_call(self):
        assert OPENCLAW_TO_WARDEN["payment.create"] == ActionType.API_CALL

    def test_email_send_maps_to_message_send(self):
        assert OPENCLAW_TO_WARDEN["email.send"] == ActionType.MESSAGE_SEND

    def test_file_read_maps_to_data_read(self):
        assert OPENCLAW_TO_WARDEN["file.read"] == ActionType.DATA_READ

    def test_browser_navigate_maps_to_api_call(self):
        assert OPENCLAW_TO_WARDEN["browser.navigate"] == ActionType.API_CALL

    def test_code_execute_maps_to_code_execute(self):
        assert OPENCLAW_TO_WARDEN["code.execute"] == ActionType.CODE_EXECUTE


class TestHighRiskActions:
    def test_email_delete_is_high_risk(self):
        assert "email.delete" in HIGH_RISK_ACTIONS

    def test_shell_execute_is_high_risk(self):
        assert "shell.execute" in HIGH_RISK_ACTIONS

    def test_payment_create_is_high_risk(self):
        assert "payment.create" in HIGH_RISK_ACTIONS

    def test_file_delete_is_high_risk(self):
        assert "file.delete" in HIGH_RISK_ACTIONS

    def test_calendar_delete_is_high_risk(self):
        assert "calendar.delete" in HIGH_RISK_ACTIONS

    def test_code_execute_is_high_risk(self):
        assert "code.execute" in HIGH_RISK_ACTIONS

    def test_email_read_is_not_high_risk(self):
        assert "email.read" not in HIGH_RISK_ACTIONS


class TestActionBridgeTranslate:
    def test_translate_preserves_openclaw_original(self):
        bridge = ActionBridge()
        action = bridge.translate(
            {"type": "email.delete", "data": {"subject": "test"}},
            {"agent_id": "bot-1"},
        )
        assert action.data["openclaw_original"] == "email.delete"
        assert action.data["subject"] == "test"

    def test_translate_sets_high_risk_context(self):
        bridge = ActionBridge()
        for oc_type in HIGH_RISK_ACTIONS:
            action = bridge.translate(
                {"type": oc_type, "data": {}},
                {"agent_id": "bot-1"},
            )
            assert action.context.get("risk") == "high", (
                f"Missing risk=high for {oc_type}"
            )

    def test_translate_normal_action_no_risk_flag(self):
        bridge = ActionBridge()
        action = bridge.translate(
            {"type": "email.read", "data": {}},
            {"agent_id": "bot-1"},
        )
        assert "risk" not in action.context

    def test_unknown_action_type_defaults_to_api_call(self):
        bridge = ActionBridge()
        action = bridge.translate(
            {"type": "unknown.action", "data": {}},
            {"agent_id": "bot-1"},
        )
        assert action.type == ActionType.API_CALL


class TestActionBridgeDecisionTranslation:
    def test_translate_decision_allow(self):
        bridge = ActionBridge()
        result = bridge.translate_decision(Decision.ALLOW, "ok")
        assert result == {"proceed": True}

    def test_translate_decision_deny(self):
        bridge = ActionBridge()
        result = bridge.translate_decision(Decision.DENY, "blocked")
        assert result["proceed"] is False
        assert result["reason"] == "blocked"
        assert result["blocked_by"] == "warden"

    def test_translate_decision_review(self):
        bridge = ActionBridge()
        result = bridge.translate_decision(Decision.REVIEW, "needs review")
        assert result["proceed"] is False
        assert result["review"] is True
        assert result["blocked_by"] == "warden"
