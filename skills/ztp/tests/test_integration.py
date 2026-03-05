import os
from scripts.shield_pro import (
    scan_file,
    scan_markdown_file,
    scan_js_file,
    scan_directory,
    scan_requirements,
    generate_markdown_report,
    scan_dynamic,
    scan_semantic,
)


def test_scan_js_file_advanced(tmp_path):
    p = tmp_path / "app.js"
    # test entropy and IPs
    p.write_text(
        "const secret = 'axz123!@#$QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm';\nconst ip = '1.2.3.4';"
    )
    findings = scan_js_file(str(p))
    assert any("high entropy" in f["issue"].lower() for f in findings)
    assert any("hardcoded ip" in f["issue"].lower() for f in findings)


def test_scan_dynamic(tmp_path):
    p = tmp_path / "detonate.py"
    # This should trigger the trap in SafeImportHarness
    p.write_text("import os\nos.system('whoami')")
    findings = scan_dynamic(str(p))
    assert any("dynamic trap" in f["issue"].lower() for f in findings)


def test_scan_semantic(tmp_path):
    p = tmp_path / "logic.py"
    p.write_text("def malicious():\n    eval('1+1')")
    # First get static findings
    static = scan_file(str(p))
    # Then semantic (as recommendation since API key is missing)
    semantic = scan_semantic(str(p), static)
    assert any("semantic review required" in f["issue"].lower() for f in semantic)


def test_generate_report_full(tmp_path):
    findings = [
        {"severity": "CRITICAL", "file": "a.py", "line": 1, "issue": "Exploit"},
        {"severity": "HIGH", "file": "b.md", "line": 0, "issue": "Phish"},
        {"severity": "MEDIUM", "file": "c.js", "line": 10, "issue": "XSS"},
        {"severity": "LOW", "file": "d.py", "line": 5, "issue": "Info"},
    ]
    report_path = tmp_path / "FULL_REPORT.md"
    generate_markdown_report(findings, str(report_path))
    content = report_path.read_text()
    assert "CRITICAL" in content
    assert "HIGH" in content
    assert "MEDIUM" in content
    assert "LOW" in content
    assert "REJECTED" in content


def test_scan_requirements_advanced(tmp_path):
    p = tmp_path / "req.txt"
    p.write_text("requests\nflsk\npandas>=1.0.0")
    findings = scan_requirements(str(p))
    assert any("typosquat" in f["issue"].lower() for f in findings)
    assert any("unpinned" in f["issue"].lower() for f in findings)
    p.write_text("requests==2.25.1\nreqests\nflask")
    findings = scan_requirements(str(p))
    assert any("typosquat risk" in f["issue"].lower() for f in findings)
    assert any("unpinned pkg" in f["issue"].lower() for f in findings)


def test_scan_python_file(tmp_path):
    p = tmp_path / "malicious.py"
    p.write_text("import os\neval(input())\nos.system('rm -rf /')")
    findings = scan_file(str(p))
    # Should catch eval (CRITICAL) and os.system (CRITICAL)
    assert any(f["severity"] == "CRITICAL" for f in findings)


def test_scan_markdown_file(tmp_path):
    p = tmp_path / "phish.md"
    # Use a raw IP and high risk TLD to trigger HIGH severity
    p.write_text(
        "[Google](http://1.2.3.4/malware)\n[Evil](https://hacked.xyz)\n<script>alert(1)</script>"
    )
    findings = scan_markdown_file(str(p))
    assert any("raw ip address" in f["issue"].lower() for f in findings)
    assert any("high-risk tld" in f["issue"].lower() for f in findings)
    assert any("script injection" in f["issue"].lower() for f in findings)


def test_scan_js_file(tmp_path):
    p = tmp_path / "xss.js"
    p.write_text("eval('evil');\ndocument.write('hacked');")
    findings = scan_js_file(str(p))
    assert any("eval detected" in f["issue"].lower() for f in findings)
    assert any("document.write used" in f["issue"].lower() for f in findings)


def test_scan_requirements(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("requests==2.25.1\nreqests\nflask")
    findings = scan_requirements(str(p))
    assert any("typosquat risk" in f["issue"].lower() for f in findings)
    assert any("unpinned pkg" in f["issue"].lower() for f in findings)


def test_generate_report(tmp_path):
    findings = [
        {"severity": "CRITICAL", "file": "test.py", "line": 1, "issue": "Exploit"}
    ]
    report_path = tmp_path / "REPORT.md"
    generate_markdown_report(findings, str(report_path))
    assert os.path.exists(report_path)
    content = report_path.read_text()
    assert "# 🛡️ Shield Pro Security Report" in content
    assert "REJECTED" in content


def test_scan_directory(tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "test_mal.py").write_text("eval(x)")
    (subdir / "readme.md").write_text("[bad](http://1.1.1.1)")

    findings = scan_directory(str(tmp_path))
    assert len(findings) >= 2
