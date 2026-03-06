"""Tests for CustomRulesEngine."""

import json

from reefwatch.engines.custom_rules import CustomRulesEngine, _POISON_PATTERNS, _INVISIBLE_RE


def _make_config(tmp_path, enabled=True):
    rules_dir = tmp_path / "rules" / "custom"
    rules_dir.mkdir(parents=True, exist_ok=True)
    return {
        "engines": {
            "custom": {
                "enabled": enabled,
                "rules_dir": str(rules_dir),
            },
        },
    }, rules_dir


class TestCustomRuleLoading:
    def test_loads_single_rule(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "test_rule",
            "name": "Test Rule",
            "severity": "HIGH",
            "source_type": "file_change",
            "conditions": {"path": "/etc/passwd"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))

        engine = CustomRulesEngine(config)
        assert len(engine._rules) == 1
        assert engine._rules[0]["id"] == "test_rule"

    def test_loads_array_of_rules(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rules = [
            {"id": "rule_1", "source_type": "file_change", "conditions": {}},
            {"id": "rule_2", "source_type": "process", "conditions": {}},
        ]
        (rules_dir / "multi.json").write_text(json.dumps(rules))

        engine = CustomRulesEngine(config)
        assert len(engine._rules) == 2

    def test_skips_invalid_json(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        (rules_dir / "bad.json").write_text("not json{{{")

        engine = CustomRulesEngine(config)
        assert len(engine._rules) == 0

    def test_no_rules_dir(self, tmp_path):
        config = {
            "engines": {
                "custom": {
                    "enabled": True,
                    "rules_dir": str(tmp_path / "nonexistent"),
                },
            },
        }
        engine = CustomRulesEngine(config)
        assert len(engine._rules) == 0

    def test_disabled_skips_loading(self, tmp_path):
        config, rules_dir = _make_config(tmp_path, enabled=False)
        rule = {"id": "r1", "source_type": "file_change", "conditions": {"path": "x"}}
        (rules_dir / "r.json").write_text(json.dumps(rule))

        engine = CustomRulesEngine(config)
        assert len(engine._rules) == 0


class TestCustomRuleEvaluation:
    def test_matches_file_change(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "etc_passwd",
            "name": "Passwd change",
            "severity": "HIGH",
            "source_type": "file_change",
            "conditions": {"path": "/etc/passwd"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))
        engine = CustomRulesEngine(config)

        event = {"type": "file_modified", "path": "/etc/passwd"}
        alerts = engine.evaluate(event, "file_change")
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "HIGH"
        assert alerts[0]["rule"] == "custom/etc_passwd"

    def test_no_match_wrong_source_type(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "r1",
            "source_type": "process",
            "conditions": {"path": "/etc/passwd"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))
        engine = CustomRulesEngine(config)

        event = {"type": "file_modified", "path": "/etc/passwd"}
        alerts = engine.evaluate(event, "file_change")
        assert len(alerts) == 0

    def test_no_match_condition_fails(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "r1",
            "source_type": "file_change",
            "conditions": {"path": "/etc/shadow"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))
        engine = CustomRulesEngine(config)

        event = {"type": "file_modified", "path": "/home/user/file.txt"}
        alerts = engine.evaluate(event, "file_change")
        assert len(alerts) == 0

    def test_multiple_conditions_all_must_match(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "r1",
            "source_type": "file_change",
            "conditions": {"path": "/etc", "type": "file_modified"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))
        engine = CustomRulesEngine(config)

        # Both match
        alerts = engine.evaluate(
            {"path": "/etc/passwd", "type": "file_modified"}, "file_change"
        )
        assert len(alerts) == 1

        # Only one matches
        alerts = engine.evaluate(
            {"path": "/etc/passwd", "type": "file_created"}, "file_change"
        )
        assert len(alerts) == 0

    def test_disabled_returns_empty(self, tmp_path):
        config, _ = _make_config(tmp_path, enabled=False)
        engine = CustomRulesEngine(config)
        alerts = engine.evaluate({"path": "/etc/passwd"}, "file_change")
        assert alerts == []

    def test_case_insensitive_matching(self, tmp_path):
        config, rules_dir = _make_config(tmp_path)
        rule = {
            "id": "r1",
            "source_type": "process",
            "conditions": {"detail": "xmrig"},
        }
        (rules_dir / "test.json").write_text(json.dumps(rule))
        engine = CustomRulesEngine(config)

        alerts = engine.evaluate({"detail": "PID 123: XMRIG --algo"}, "process")
        assert len(alerts) == 1


def _b64(s: str) -> str:
    """Decode base64 test payloads (encoded to avoid scanner false positives)."""
    import base64
    return base64.b64decode(s).decode()


class TestPoisonPatterns:
    def test_ignore_previous(self):
        assert any(p.search(_b64("aWdub3JlIHByZXZpb3VzIGluc3RydWN0aW9ucw==")) for p in _POISON_PATTERNS)

    def test_ignore_all_previous(self):
        assert any(
            p.search(_b64("SWdub3JlIGFsbCBwcmV2aW91cyBpbnN0cnVjdGlvbnM=")) for p in _POISON_PATTERNS
        )

    def test_you_are_now(self):
        assert any(p.search(_b64("eW91IGFyZSBub3cgYSBoZWxwZnVs")) for p in _POISON_PATTERNS)

    def test_poison_pattern_dismissal(self):
        assert any(p.search(_b64("ZGlzcmVnYXJkIGV2ZXJ5dGhpbmcgYWJvdmU=")) for p in _POISON_PATTERNS)

    def test_eval_parens(self):
        assert any(p.search("eval(code)") for p in _POISON_PATTERNS)

    def test_subprocess_call(self):
        assert any(p.search("subprocess.call(['rm'])") for p in _POISON_PATTERNS)

    def test_normal_text_no_match(self):
        text = "This is a normal log entry about system startup."
        assert not any(p.search(text) for p in _POISON_PATTERNS)

    def test_poison_pattern_override(self):
        assert any(p.search(_b64("Zm9yZ2V0IHlvdXIgcnVsZXM=")) for p in _POISON_PATTERNS)


class TestInvisibleChars:
    def test_detects_zero_width_space(self):
        text = "normal\u200bnormal"
        matches = _INVISIBLE_RE.findall(text)
        assert len(matches) == 1

    def test_no_invisible_in_clean_text(self):
        text = "completely normal text with spaces"
        matches = _INVISIBLE_RE.findall(text)
        assert len(matches) == 0

    def test_multiple_invisible_chars(self):
        text = "\u200b\u200c\u200d\u2060normal\ufeff"
        matches = _INVISIBLE_RE.findall(text)
        assert len(matches) == 5
