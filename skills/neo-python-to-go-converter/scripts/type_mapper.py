#!/usr/bin/env python3
"""
type_mapper.py — Python-to-Go type mapping and inference.

Usage:
  This module is imported by converter and go_generator.
  It provides functions to infer Go types from Python AST nodes and
  to map known Python types to Go equivalents.
"""

import json
import os
from typing import Any, Dict, Optional

# Load reference mappings
REFERENCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')
MAPPINGS_PATH = os.path.join(REFERENCES_DIR, 'python_to_go_mappings.json')

with open(MAPPINGS_PATH, 'r') as f:
    MAPPINGS = json.load(f)

TYPE_MAP = MAPPINGS.get('types', {})
OPERATOR_MAP = MAPPINGS.get('operators', {})
FUNCTION_MAP = MAPPINGS.get('functions', {})


def map_python_type_to_go(py_type: str) -> str:
    """Map a known Python type name to its Go equivalent."""
    if py_type in TYPE_MAP:
        return TYPE_MAP[py_type]
    # Fallback: empty interface
    return "interface{}"


def infer_type_from_constant(node: Any) -> Optional[str]:
    """Infer Go type from a Python AST constant node."""
    import ast
    if isinstance(node, ast.Constant):
        value = node.value
        if value is None:
            return "interface{}"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float64"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, bytes):
            return "[]byte"
    elif isinstance(node, ast.List):
        # Try to infer element type from first element if present
        if node.elts:
            inner_type = infer_type(node.elts[0])
            return f"[]{inner_type}" if inner_type else "[]interface{}"
        return "[]interface{}"
    elif isinstance(node, ast.Dict):
        # Attempt to infer key/value types from first pair if present
        if node.keys and node.values:
            key_type = infer_type(node.keys[0])
            val_type = infer_type(node.values[0])
            if key_type and val_type:
                return f"map[{key_type}]{val_type}"
        return "map[string]interface{}"
    elif isinstance(node, ast.Tuple):
        # Tuple becomes struct or multiple return? For now, interface{}
        return "interface{}"
    return None


def infer_type(node: Any, local_vars: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Infer Go type for a Python AST node, optionally using known local variable types.
    Returns a Go type string or None if unknown.
    """
    import ast

    # Constant
    if isinstance(node, ast.Constant):
        return infer_type_from_constant(node)

    # Name (variable)
    if isinstance(node, ast.Name):
        var_name = node.id
        if local_vars and var_name in local_vars:
            return local_vars[var_name]
        # Default unknown variable is interface{}
        return "interface{}"

    # Call
    if isinstance(node, ast.Call):
        # Built-in functions mapping
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in FUNCTION_MAP:
                # For built-in functions, we might know return type
                mapped = FUNCTION_MAP[func_name]
                if mapped == "len":
                    # len returns int
                    return "int"
                elif mapped == "range":
                    # range returns an iterator; for simplicity, return int
                    return "int"
        # Unknown call returns interface{}
        return "interface{}"

    # BinaryOp
    if isinstance(node, ast.BinOp):
        left_type = infer_type(node.left, local_vars)
        right_type = infer_type(node.right, local_vars)
        if left_type and right_type and left_type == right_type:
            # Operator result type usually matches operand type for numeric ops
            op = type(node.op).__name__
            if op in ('Add', 'Sub', 'Mult', 'Div', 'Mod'):
                return left_type
            # For string concatenation, Add can keep string
            if op == 'Add' and left_type == "string":
                return "string"
        # Fallback: use left_type or interface{}
        return left_type or "interface{}"

    # Compare
    if isinstance(node, ast.Compare):
        # Comparison returns bool
        return "bool"

    # BoolOp (and/or)
    if isinstance(node, ast.BoolOp):
        return "bool"

    # UnaryOp
    if isinstance(node, ast.UnaryOp):
        operand_type = infer_type(node.operand, local_vars)
        op = type(node.op).__name__
        if op == 'Not':
            return "bool"
        return operand_type

    # ListComp, GeneratorExp? Not fully supported, return interface{}
    # Attribute access
    if isinstance(node, ast.Attribute):
        # Could potentially look up attribute type, but not implemented.
        return "interface{}"

    # Subscript (indexing)
    if isinstance(node, ast.Subscript):
        # If value is a list or dict, return element type
        value_type = infer_type(node.value, local_vars)
        if value_type:
            if value_type.startswith("[]"):
                return value_type[2:]  # strip [] 
            if value_type.startswith("map["):
                # map[K]V returns V
                end = value_type.find(']')
                if end != -1:
                    return value_type[end+1:]
        return "interface{}"

    return None


def get_go_type_name(py_type_name: str) -> str:
    """Get Go type string for a Python type name (as declared in code)."""
    return map_python_type_to_go(py_type_name)


def operator_to_go(op_name: str) -> str:
    """Map Python AST operator name to Go operator."""
    return OPERATOR_MAP.get(op_name, op_name)


def builtin_to_go(func_name: str) -> Optional[str]:
    """Map Python built-in function name to Go equivalent."""
    return FUNCTION_MAP.get(func_name)