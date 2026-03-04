from actions.start_call import build_operator_summary


def test_summary_dry_run_format():
    result = {
        "dry_run": True,
        "mode": "agent",
        "destination_masked": "***0123",
    }
    summary = build_operator_summary(result)
    assert summary == "OUTCOME: dry_run (no execution) | mode=agent | to=***0123"


def test_summary_non_definitive_answered_format():
    result = {
        "dry_run": False,
        "mode": "agent",
        "destination_masked": "***0123",
        "call_outcome": {
            "state": "answered",
            "definitive": False,
            "success": None,
        },
    }
    summary = build_operator_summary(result)
    assert summary == "OUTCOME: answered (non_definitive) | mode=agent | to=***0123"


def test_summary_ambiguous_local_connected_note():
    result = {
        "dry_run": False,
        "mode": "agent",
        "destination_masked": "***5678",
        "call_outcome": {
            "state": "agent_connected_local",
            "definitive": False,
            "success": None,
            "note": "Local media/session connected, but destination-level success is not yet definitive",
        },
    }
    summary = build_operator_summary(result)
    assert summary == (
        "OUTCOME: agent_connected_local (non_definitive) | mode=agent | to=***5678"
        " | note=Local media/session connected, but destination-level success is not yet definitive"
    )


def test_summary_payload_fallback_format():
    result = {
        "dry_run": False,
        "mode": "callback",
        "destination_masked": "***9999",
        "payload": {"status": "queued"},
    }
    summary = build_operator_summary(result)
    assert summary == "OUTCOME: queued (from_payload) | mode=callback | to=***9999"
