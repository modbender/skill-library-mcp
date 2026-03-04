#!/usr/bin/env python3
"""
Core analysis engine for detecting memory issues in Python code.

Usage:
    from analyzer import analyze_source
    issues = analyze_source(source_code, filename)

The analyzer walks the AST and produces a list of issue dictionaries.
"""

import ast
import os
import sys
from typing import List, Dict, Any, Union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import utils


class Analyzer(ast.NodeVisitor):
    """
    AST visitor that collects potential memory issues from Python source code.

    Detected patterns:
    - unclosed_file: open() without context manager
    - large_list_comprehension: list comprehensions that may be replaceable with generators
    - string_concat_in_loop: string concatenation inside loops
    - mutable_default_arg: mutable default arguments in function definitions
    - global_container_append: appending to module-level mutable containers
    - unnecessary_list_call: list() wrapping a generator where not needed
    """

    def __init__(self, source: str, filename: str):
        self.source = source
        self.filename = filename
        self.issues: List[Dict[str, Any]] = []
        self._parents: Dict[int, ast.AST] = {}

    def _build_parent_map(self, tree: ast.AST):
        """Build a mapping from child node id to parent node."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self._parents[id(child)] = node

    def _get_parent(self, node: ast.AST):
        """Get the parent node of the given node."""
        return self._parents.get(id(node))

    def _is_inside_with(self, node: ast.AST) -> bool:
        """Check if a node is the context_expr of a withitem."""
        parent = self._get_parent(node)
        if isinstance(parent, ast.withitem) and parent.context_expr is node:
            return True
        return False

    def _is_inside_loop(self, node: ast.AST) -> bool:
        """Check if a node is inside a for or while loop."""
        current = node
        while current is not None:
            current = self._get_parent(current)
            if isinstance(current, (ast.For, ast.While, ast.AsyncFor)):
                return True
        return False

    def _get_enclosing_scope_type(self, node: ast.AST) -> str:
        """Return 'module', 'class', or 'function' for the enclosing scope."""
        current = node
        while current is not None:
            current = self._get_parent(current)
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return "function"
            if isinstance(current, ast.ClassDef):
                return "class"
            if isinstance(current, ast.Module):
                return "module"
        return "module"

    # --- Detectors ---

    def visit_Call(self, node: ast.Call):
        self._check_unclosed_file(node)
        self._check_unnecessary_list_call(node)
        self.generic_visit(node)

    def _check_unclosed_file(self, node: ast.Call):
        """Detect open() calls not wrapped in a with statement."""
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if not self._is_inside_with(node):
                snippet = utils.get_source_segment(self.source, node)
                file_arg = None
                if (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    file_arg = node.args[0].value
                self.issues.append(
                    {
                        "type": "unclosed_file",
                        "file": self.filename,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "code_snippet": snippet,
                        "message": "open() called without a context manager (with statement). "
                        "This risks file descriptor leaks.",
                        "severity": "high",
                        "file_arg": file_arg,
                    }
                )

    def _check_unnecessary_list_call(self, node: ast.Call):
        """Detect list() wrapping a generator expression when the list may not be needed."""
        if isinstance(node.func, ast.Name) and node.func.id == "list":
            if len(node.args) == 1 and isinstance(node.args[0], ast.GeneratorExp):
                snippet = utils.get_source_segment(self.source, node)
                self.issues.append(
                    {
                        "type": "unnecessary_list_call",
                        "file": self.filename,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "code_snippet": snippet,
                        "message": "list() wrapping a generator expression materializes all items. "
                        "If consumed once, keep as generator.",
                        "severity": "low",
                    }
                )

    def visit_ListComp(self, node: ast.ListComp):
        """Detect list comprehensions that could be generator expressions."""
        size_estimate: Union[int, str] = "unknown"
        if node.generators:
            size_estimate = self._estimate_iterable_size(node.generators[0].iter)

        severity = "low"
        if size_estimate == "unknown":
            severity = "medium"
        elif isinstance(size_estimate, int):
            if size_estimate > 10000:
                severity = "high"
            elif size_estimate > 1000:
                severity = "medium"

        snippet = utils.get_source_segment(self.source, node)
        self.issues.append(
            {
                "type": "large_list_comprehension",
                "file": self.filename,
                "line": node.lineno,
                "col": node.col_offset,
                "code_snippet": snippet,
                "message": f"List comprehension creates a full list in memory. Estimated size: {size_estimate}.",
                "severity": severity,
                "size_estimate": size_estimate,
            }
        )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        """Detect string concatenation with += inside loops."""
        if isinstance(node.op, ast.Add) and self._is_inside_loop(node):
            # Heuristic: target is a simple name (str concat is common with +=)
            if isinstance(node.target, ast.Name):
                snippet = utils.get_source_segment(self.source, node)
                self.issues.append(
                    {
                        "type": "string_concat_in_loop",
                        "file": self.filename,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "code_snippet": snippet,
                        "message": "Possible string concatenation with += inside a loop. "
                        "Strings are immutable; each += creates a new object. "
                        "Consider collecting parts in a list and using ''.join().",
                        "severity": "medium",
                    }
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_mutable_defaults(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_mutable_defaults(node)
        self.generic_visit(node)

    def _check_mutable_defaults(self, node):
        """Detect mutable default arguments (list, dict, set literals)."""
        for default in node.args.defaults + node.args.kw_defaults:
            if default is None:
                continue
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                snippet = utils.get_source_segment(self.source, default)
                self.issues.append(
                    {
                        "type": "mutable_default_arg",
                        "file": self.filename,
                        "line": default.lineno,
                        "col": default.col_offset,
                        "code_snippet": snippet,
                        "message": "Mutable default argument detected. "
                        "This object is shared across all calls and can accumulate data, "
                        "causing unexpected memory growth.",
                        "severity": "high",
                    }
                )

    def visit_Attribute(self, node: ast.Attribute):
        """Detect appending to module-level containers inside functions."""
        if node.attr in ("append", "extend", "add", "update"):
            if isinstance(node.value, ast.Name):
                scope = self._get_enclosing_scope_type(node)
                if scope == "function":
                    var_name = node.value.id
                    func_node = self._get_enclosing_function(node)
                    if func_node and not self._is_local_name(func_node, var_name):
                        parent = self._get_parent(node)
                        if isinstance(parent, ast.Call):
                            snippet = utils.get_source_segment(self.source, parent)
                            self.issues.append(
                                {
                                    "type": "global_container_append",
                                    "file": self.filename,
                                    "line": node.lineno,
                                    "col": node.col_offset,
                                    "code_snippet": snippet,
                                    "message": f"Calling .{node.attr}() on '{var_name}' inside a function. "
                                    "If this is a module-level container, repeated calls will "
                                    "accumulate data and grow memory indefinitely.",
                                    "severity": "medium",
                                }
                            )
        self.generic_visit(node)

    def _get_enclosing_function(self, node: ast.AST):
        """Return the nearest enclosing FunctionDef/AsyncFunctionDef, or None."""
        current = node
        while current is not None:
            current = self._get_parent(current)
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return current
        return None

    def _is_local_name(self, func_node, name: str) -> bool:
        """Check if `name` is a parameter or locally assigned variable in the function."""
        # Check parameters
        for arg in func_node.args.args + func_node.args.posonlyargs + func_node.args.kwonlyargs:
            if arg.arg == name:
                return True
        if func_node.args.vararg and func_node.args.vararg.arg == name:
            return True
        if func_node.args.kwarg and func_node.args.kwarg.arg == name:
            return True
        # Check local assignments (direct children of the function body)
        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return True
            elif isinstance(stmt, (ast.For, ast.AsyncFor)):
                if isinstance(stmt.target, ast.Name) and stmt.target.id == name:
                    return True
        return False

    # --- Helpers ---

    def _estimate_iterable_size(self, iter_node: ast.AST) -> Union[int, str]:
        """
        Estimate the number of items in the iterable used in a comprehension.
        Returns an integer if estimable, else 'unknown'.
        """
        try:
            if isinstance(iter_node, (ast.List, ast.Tuple)):
                return len(iter_node.elts)
            if (
                isinstance(iter_node, ast.Call)
                and isinstance(iter_node.func, ast.Name)
                and iter_node.func.id == "range"
            ):
                args = iter_node.args
                if not args:
                    return "unknown"

                def eval_int(n: ast.AST) -> int:
                    if isinstance(n, ast.Constant) and isinstance(n.value, int):
                        return n.value
                    raise ValueError("Non-constant integer")

                start = 0
                stop = None
                step = 1
                if len(args) == 1:
                    stop = eval_int(args[0])
                elif len(args) >= 2:
                    start = eval_int(args[0])
                    stop = eval_int(args[1])
                if len(args) >= 3:
                    step = eval_int(args[2])
                if stop is None or step == 0:
                    return "unknown"
                size = max(0, (stop - start + (step - (1 if step > 0 else -1))) // step)
                return size
        except Exception:
            return "unknown"
        return "unknown"


def analyze_source(source: str, filename: str) -> List[Dict[str, Any]]:
    """
    Parse and analyze a Python source string.
    Returns a list of issue dictionaries.
    """
    tree = ast.parse(source, filename=filename)
    a = Analyzer(source, filename)
    a._build_parent_map(tree)
    a.visit(tree)
    return a.issues
