import pytest
from scripts.core import scrub_data, add_insight, start_project, get_insights
import scripts.db as db
import json
import os

def test_scrub_data_urls():
    url = "https://user:password@example.com/api?token=secret123&other=val"
    scrubbed = scrub_data(url)
    assert "user:password" not in scrubbed
    assert "secret123" not in scrubbed
    assert "REDACTED" in scrubbed

def test_scrub_data_paths():
    path = "/Users/luka/secret/project/key.pem"
    scrubbed = scrub_data(path)
    assert "/Users/luka" not in scrubbed
    assert "[REDACTED_PATH]" in scrubbed

def test_add_insight_scrubbing():
    # Setup
    db.init_db()
    project_id = "scrub-test"
    start_project(project_id, "Scrub Test", "Objective", silent=True)
    
    secret_url = "http://admin:12345@site.com/?api_key=abcdef"
    secret_content = "My path is /Users/kalle/config.json"
    
    add_insight(project_id, "Secret Title", secret_content, source_url=secret_url)
    
    insights = get_insights(project_id)
    title, content, evidence, tags, created_at, confidence = insights[0]
    
    ev_json = json.loads(evidence)
    assert "12345" not in ev_json["source_url"]
    assert "abcdef" not in ev_json["source_url"]
    assert "REDACTED" in ev_json["source_url"]
    assert "/Users/kalle" not in content
    assert "[REDACTED_PATH]" in content
