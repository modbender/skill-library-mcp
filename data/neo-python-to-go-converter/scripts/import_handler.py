#!/usr/bin/env python3
"""
import_handler.py — Python import translation to Go import paths.

Usage:
  This module is imported by converter and go_generator.
  It provides functions to map Python module names to Go import paths.
"""

import json
import os
from typing import Dict, List, Set

REFERENCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')
STDLIB_EQUIV_PATH = os.path.join(REFERENCES_DIR, 'stdlib_equivalents.json')

with open(STDLIB_EQUIV_PATH, 'r') as f:
    STDLIB_MAP = json.load(f)


def translate_import(module_name: str) -> Optional[str]:
    """
    Translate a Python module name to its Go import path.
    Returns None if there is no known mapping and the module should be flagged.
    """
    return STDLIB_MAP.get(module_name)


def collect_imports_from_ast(ast_tree: Any) -> Set[str]:
    """
    Walk an AST and collect all imported module names.
    Returns a set of module names.
    """
    import ast
    modules = set()

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                modules.add(alias.name.split('.')[0])
        def visit_ImportFrom(self, node):
            if node.module:
                modules.add(node.module.split('.')[0])

    ImportVisitor().visit(ast_tree)
    return modules


def get_required_go_imports(modules: Set[str]) -> List[str]:
    """
    Given a set of Python module names, return a list of Go import paths
    that are needed. Only includes mappings that are known.
    """
    imports = []
    for mod in sorted(modules):
        go_path = translate_import(mod)
        if go_path:
            imports.append(go_path)
    return imports