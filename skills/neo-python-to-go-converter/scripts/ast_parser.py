#!/usr/bin/env python3
"""
ast_parser.py — Parse Python source code into an intermediate representation.

Usage:
  This module is imported by the converter.
  parse(source_code) returns a list of statement dictionaries representing the module.
"""

import ast
from typing import Any, Dict, List, Optional, Union

# AST node types we'll produce:
# {'type': 'function', 'name': str, 'args': [{'name': str, 'type': str?}], 'body': [stmt], 'decorators': []}
# {'type': 'class', 'name': str, 'bases': [], 'body': [stmt]}
# {'type': 'assign', 'targets': [{'type': 'name', 'id': str}], 'value': expr}
# {'type': 'aug_assign', 'target': target, 'op': str, 'value': value}
# {'type': 'if', 'test': expr, 'body': [stmt], 'orelse': [stmt]}
# {'type': 'for', 'target': target, 'iter': expr, 'body': [stmt], 'orelse': [stmt]}
# {'type': 'while', 'test': expr, 'body': [stmt], 'orelse': [stmt]}
# {'type': 'return', 'value': expr}
# {'type': 'expr', 'value': expr} (expression statement)
# {'type': 'pass'}
# {'type': 'delete', 'targets': [target]}

# Expressions:
# {'type': 'name', 'id': str}
# {'type': 'constant', 'value': Any}
# {'type': 'call', 'func': expr, 'args': [expr], 'keywords': [{arg: name, value: expr}]}
# {'type': 'attribute', 'value': expr, 'attr': str}
# {'type': 'binop', 'left': expr, 'op': str, 'right': expr}
# {'type': 'unaryop', 'op': str, 'operand': expr}
# {'type': 'compare', 'left': expr, 'ops': [str], 'comparators': [expr]}
# {'type': 'boolop', 'op': str, 'values': [expr]}
# {'type': 'list', 'elts': [expr]}
# {'type': 'dict', 'keys': [expr], 'values': [expr]}
# {'type': 'tuple', 'elts': [expr]}
# {'type': 'subscript', 'value': expr, 'slice': expr}
# {'type': 'lambda', 'args': [arg], 'body': expr}


def parse(source: str) -> List[Dict[str, Any]]:
    """Parse Python source code and return an intermediate representation."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in Python code: {e}")

    return _parse_statements(tree.body)


def _parse_statements(stmts: List[ast.stmt]) -> List[Dict[str, Any]]:
    return [_parse_stmt(s) for s in stmts]


def _parse_stmt(stmt: ast.stmt) -> Dict[str, Any]:
    if isinstance(stmt, ast.FunctionDef):
        return _parse_functiondef(stmt)
    if isinstance(stmt, ast.AsyncFunctionDef):
        # async not supported
        return {'type': 'unsupported', 'feature': 'async function'}
    if isinstance(stmt, ast.ClassDef):
        return _parse_classdef(stmt)
    if isinstance(stmt, ast.Return):
        return {'type': 'return', 'value': _parse_expr(stmt.value) if stmt.value else None}
    if isinstance(stmt, ast.Delete):
        return {'type': 'delete', 'targets': [_parse_expr(t) for t in stmt.targets]}
    if isinstance(stmt, ast.Assign):
        return _parse_assign(stmt)
    if isinstance(stmt, ast.AugAssign):
        return _parse_aug_assign(stmt)
    if isinstance(stmt, ast.If):
        return _parse_if(stmt)
    if isinstance(stmt, ast.For):
        return _parse_for(stmt)
    if isinstance(stmt, ast.AsyncFor):
        return {'type': 'unsupported', 'feature': 'async for'}
    if isinstance(stmt, ast.While):
        return _parse_while(stmt)
    if isinstance(stmt, ast.With):
        return {'type': 'unsupported', 'feature': 'with statement'}
    if isinstance(stmt, ast.AsyncWith):
        return {'type': 'unsupported', 'feature': 'async with'}
    if isinstance(stmt, ast.Raise):
        return _parse_raise(stmt)
    if isinstance(stmt, ast.Try):
        return _parse_try(stmt)
    if isinstance(stmt, ast.Assert):
        return _parse_assert(stmt)
    if isinstance(stmt, ast.Expr):
        return {'type': 'expr', 'value': _parse_expr(stmt.value)}
    if isinstance(stmt, ast.Pass):
        return {'type': 'pass'}
    if isinstance(stmt, ast.Break):
        return {'type': 'break'}
    if isinstance(stmt, ast.Continue):
        return {'type': 'continue'}
    # Unknown
    return {'type': 'unsupported', 'feature': type(stmt).__name__}


def _parse_functiondef(node: ast.FunctionDef) -> Dict[str, Any]:
    args = []
    for arg in node.args.args:
        # arg is ast.arg
        arg_name = arg.arg
        # try to get annotation
        arg_type = None
        if arg.annotation:
            arg_type = _parse_expr(arg.annotation)
        args.append({'name': arg_name, 'type': arg_type})
    # vararg, kwonlyargs, kwarg, kw_defaults omitted for brevity
    returns = None
    if node.returns:
        returns = _parse_expr(node.returns)
    body = _parse_statements(node.body)
    decorators = [_parse_expr(d) for d in node.decorator_list]
    return {
        'type': 'function',
        'name': node.name,
        'args': args,
        'body': body,
        'decorators': decorators,
        'returns': returns
    }


def _parse_classdef(node: ast.ClassDef) -> Dict[str, Any]:
    bases = [_parse_expr(b) for b in node.bases]
    body = _parse_statements(node.body)
    return {
        'type': 'class',
        'name': node.name,
        'bases': bases,
        'body': body
    }


def _parse_assign(node: ast.Assign) -> Dict[str, Any]:
    targets = [_parse_expr(t) for t in node.targets]
    value = _parse_expr(node.value)
    return {'type': 'assign', 'targets': targets, 'value': value}


def _parse_aug_assign(node: ast.AugAssign) -> Dict[str, Any]:
    target = _parse_expr(node.target)
    op = type(node.op).__name__
    value = _parse_expr(node.value)
    return {'type': 'aug_assign', 'target': target, 'op': op, 'value': value}


def _parse_if(node: ast.If) -> Dict[str, Any]:
    test = _parse_expr(node.test)
    body = _parse_statements(node.body)
    orelse = _parse_statements(node.orelse)
    return {'type': 'if', 'test': test, 'body': body, 'orelse': orelse}


def _parse_for(node: ast.For) -> Dict[str, Any]:
    target = _parse_expr(node.target)
    iter = _parse_expr(node.iter)
    body = _parse_statements(node.body)
    orelse = _parse_statements(node.orelse)
    return {'type': 'for', 'target': target, 'iter': iter, 'body': body, 'orelse': orelse}


def _parse_while(node: ast.While) -> Dict[str, Any]:
    test = _parse_expr(node.test)
    body = _parse_statements(node.body)
    orelse = _parse_statements(node.orelse)
    return {'type': 'while', 'test': test, 'body': body, 'orelse': orelse}


def _parse_raise(node: ast.Raise) -> Dict[str, Any]:
    exc = _parse_expr(node.exc) if node.exc else None
    cause = _parse_expr(node.cause) if node.cause else None
    return {'type': 'raise', 'exc': exc, 'cause': cause}


def _parse_try(node: ast.Try) -> Dict[str, Any]:
    body = _parse_statements(node.body)
    handlers = []
    for h in node.handlers:
        h_type = _parse_expr(h.type) if h.type else None
        h_name = h.name
        h_body = _parse_statements(h.body)
        handlers.append({'type': h_type, 'name': h_name, 'body': h_body})
    orelse = _parse_statements(node.orelse)
    finalbody = _parse_statements(node.finalbody)
    return {
        'type': 'try',
        'body': body,
        'handlers': handlers,
        'orelse': orelse,
        'finalbody': finalbody
    }


def _parse_assert(node: ast.Assert) -> Dict[str, Any]:
    test = _parse_expr(node.test)
    msg = _parse_expr(node.msg) if node.msg else None
    return {'type': 'assert', 'test': test, 'msg': msg}


def _parse_expr(expr: ast.expr) -> Dict[str, Any]:
    if isinstance(expr, ast.Constant):
        # Handle None, bool, int, float, str, bytes, Ellipsis
        value = expr.value
        if value is ...:
            value = 'Ellipsis'
        return {'type': 'constant', 'value': value}
    if isinstance(expr, ast.Name):
        return {'type': 'name', 'id': expr.id}
    if isinstance(expr, ast.Call):
        return _parse_call(expr)
    if isinstance(expr, ast.Attribute):
        return {'type': 'attribute', 'value': _parse_expr(expr.value), 'attr': expr.attr}
    if isinstance(expr, ast.BinOp):
        left = _parse_expr(expr.left)
        op = type(expr.op).__name__
        right = _parse_expr(expr.right)
        return {'type': 'binop', 'left': left, 'op': op, 'right': right}
    if isinstance(expr, ast.UnaryOp):
        op = type(expr.op).__name__
        operand = _parse_expr(expr.operand)
        return {'type': 'unaryop', 'op': op, 'operand': operand}
    if isinstance(expr, ast.Compare):
        left = _parse_expr(expr.left)
        ops = [type(op).__name__ for op in expr.ops]
        comparators = [_parse_expr(c) for c in expr.comparators]
        return {'type': 'compare', 'left': left, 'ops': ops, 'comparators': comparators}
    if isinstance(expr, ast.BoolOp):
        op = type(expr.op).__name__
        values = [_parse_expr(v) for v in expr.values]
        return {'type': 'boolop', 'op': op, 'values': values}
    if isinstance(expr, ast.List):
        elts = [_parse_expr(e) for e in expr.elts]
        return {'type': 'list', 'elts': elts}
    if isinstance(expr, ast.Tuple):
        elts = [_parse_expr(e) for e in expr.elts]
        return {'type': 'tuple', 'elts': elts}
    if isinstance(expr, ast.Dict):
        keys = [_parse_expr(k) for k in expr.keys]
        values = [_parse_expr(v) for v in expr.values]
        return {'type': 'dict', 'keys': keys, 'values': values}
    if isinstance(expr, ast.Subscript):
        value = _parse_expr(expr.value)
        slice = _parse_expr(expr.slice)
        return {'type': 'subscript', 'value': value, 'slice': slice}
    if isinstance(expr, ast.Lambda):
        args = []
        for arg in expr.args.args:
            args.append({'name': arg.arg})
        body = _parse_expr(expr.body)
        return {'type': 'lambda', 'args': args, 'body': body}
    if isinstance(expr, ast.ListComp):
        return {'type': 'unsupported', 'feature': 'list comprehension'}
    if isinstance(expr, ast.SetComp):
        return {'type': 'unsupported', 'feature': 'set comprehension'}
    if isinstance(expr, ast.DictComp):
        return {'type': 'unsupported', 'feature': 'dict comprehension'}
    if isinstance(expr, ast.GeneratorExp):
        return {'type': 'unsupported', 'feature': 'generator expression'}
    # Yield, Await, etc.
    return {'type': 'unsupported', 'feature': type(expr).__name__}


def _parse_call(expr: ast.Call) -> Dict[str, Any]:
    func = _parse_expr(expr.func)
    args = [_parse_expr(a) for a in expr.args]
    keywords = []
    for kw in expr.keywords:
        keywords.append({'arg': kw.arg, 'value': _parse_expr(kw.value)})
    return {'type': 'call', 'func': func, 'args': args, 'keywords': keywords}