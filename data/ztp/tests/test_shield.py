import ast
from scripts.shield_pro import ShieldPro20


def test_shield_safe_constant():
    visitor = ShieldPro20("test.py")
    # Test safe constant detection
    node_const = ast.Constant(value="safe")
    assert visitor._is_safe_constant(node_const) is True

    node_binop = ast.BinOp(
        left=ast.Constant(value="a"), op=ast.Add(), right=ast.Constant(value="b")
    )
    assert visitor._is_safe_constant(node_binop) is True


def test_shield_forbidden_calls():
    visitor = ShieldPro20("test.py")
    source = "eval('1+1')\nos.system('ls')\nexec(user_input)"
    tree = ast.parse(source)
    visitor.visit(tree)

    findings = visitor.report
    # eval('1+1') should be LOW (safe constant)
    assert any(f["severity"] == "LOW" and "eval" in f["issue"] for f in findings)
    # os.system('ls') should be LOW (safe constant)
    assert any(f["severity"] == "LOW" and "os.system" in f["issue"] for f in findings)
    # exec(user_input) should be CRITICAL
    assert any(f["severity"] == "CRITICAL" and "exec" in f["issue"] for f in findings)


def test_shield_obfuscation_partial():
    visitor = ShieldPro20("test.py")
    source = "from functools import partial\nimport subprocess\nrunner = partial(subprocess.Popen, shell=True)\nrunner('ls')"
    tree = ast.parse(source)
    visitor.visit(tree)

    findings = visitor.report
    assert any(
        "Obfuscated call via partial(): subprocess.Popen" in f["issue"]
        for f in findings
    )


def test_shield_dynamic_imports():
    visitor = ShieldPro20("test.py")
    source = "__import__('os')"
    tree = ast.parse(source)
    visitor.visit(tree)

    assert any("__import__" in f["issue"] for f in visitor.report)


def test_shield_aliases():
    visitor = ShieldPro20("test.py")
    source = "import os as system_hacker\nsystem_hacker.popen('whoami')"
    tree = ast.parse(source)
    visitor.visit(tree)

    assert any("os.popen" in f["issue"] for f in visitor.report)


def test_shield_imports():
    visitor = ShieldPro20("test.py")
    source = "import socket\nfrom subprocess import Popen as P"
    visitor.visit(ast.parse(source))
    assert any("socket" in f["issue"] for f in visitor.report)
    assert visitor.import_aliases["P"] == "subprocess.Popen"


def test_shield_high_entropy():
    visitor = ShieldPro20("test.py")
    # A pseudo-random looking high entropy string
    source = "PAYLOAD = 'axz123!@#$QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890'"
    visitor.visit(ast.parse(source))
    assert any("High entropy" in f["issue"] for f in visitor.report)


def test_shield_metaprogramming():
    visitor = ShieldPro20("test.py")
    source = "obj.__subclasses__()"
    visitor.visit(ast.parse(source))
    assert any("Metaprogramming" in f["issue"] for f in visitor.report)

def test_shield_safe_list_constant():
    visitor = ShieldPro20("test.py")
    source = "eval('[1, 2, 3]')"
    visitor.visit(ast.parse(source))
    # Should be LOW severity because it's a safe constant list
    assert any(f["severity"] == "LOW" and "eval" in f["issue"] for f in visitor.report)

def test_shield_string_ips_urls():
    visitor = ShieldPro20("test.py")
    # Entropy + IP + URL in one string to hit multiple lines
    source = "DATA = 'This is a very long string with an IP 192.168.1.1 and a URL http://malicious.com/?q=payload&entropy=high1234567890'"
    visitor.visit(ast.parse(source))
    # Verify IP and URL detection inside visit_Constant
    assert any("Hardcoded IP" in f["issue"] for f in visitor.report)
    assert any("Hardcoded URL" in f["issue"] for f in visitor.report)
