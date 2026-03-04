#!/usr/bin/env python3
"""
go_generator.py — Generate idiomatic Go code from the parsed intermediate representation.

Usage:
  This module is imported by converter.
  GoGenerator(ir).generate() returns a Go source string.
"""

import json
import os
from typing import Any, Dict, List, Optional, Set

from type_mapper import infer_type, map_python_type_to_go, operator_to_go, builtin_to_go
from import_handler import get_required_go_imports, collect_imports_from_ast
import ast

# We need access to the original AST to collect import statements, but our IR loses that.
# We'll modify converter to pass the original AST or the collected imports. For now, we'll
# have go_generator accept an optional set of required imports.

REFERENCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')
MAPPINGS_PATH = os.path.join(REFERENCES_DIR, 'python_to_go_mappings.json')

with open(MAPPINGS_PATH, 'r') as f:
    MAPPINGS = json.load(f)

FUNCTION_MAP = MAPPINGS.get('functions', {})


class GoGenerator:
    def __init__(self, ir: List[Dict[str, Any]], required_imports: Optional[Set[str]] = None):
        self.ir = ir
        self.required_imports = required_imports or set()
        self.output_lines: List[str] = []
        self.indent_level = 0
        self.known_vars: Dict[str, str] = {}  # variable name -> Go type (for current scope)

    def generate(self) -> str:
        # Start with package declaration: default "package main"
        self.output_lines.append("package main")
        self.output_lines.append("")

        # Add imports if any
        if self.required_imports:
            import_lines = []
            for imp in sorted(self.required_imports):
                import_lines.append(f'\t"{imp}"')
            self.output_lines.append("import (")
            self.output_lines.extend(import_lines)
            self.output_lines.append(")")
            self.output_lines.append("")

        # Process top-level statements
        for stmt in self.ir:
            self._generate_stmt(stmt)
            if stmt.get('type') not in ('function', 'class'):
                # Ensure separation between statements
                pass

        return "\n".join(self.output_lines)

    def _generate_stmt(self, stmt: Dict[str, Any]):
        stmt_type = stmt.get('type')
        if stmt_type == 'function':
            self._generate_function(stmt)
        elif stmt_type == 'class':
            self._generate_class(stmt)
        elif stmt_type == 'assign':
            self._generate_assign(stmt)
        elif stmt_type == 'aug_assign':
            self._generate_aug_assign(stmt)
        elif stmt_type == 'if':
            self._generate_if(stmt)
        elif stmt_type == 'for':
            self._generate_for(stmt)
        elif stmt_type == 'while':
            self._generate_while(stmt)
        elif stmt_type == 'return':
            self._generate_return(stmt)
        elif stmt_type == 'expr':
            self._generate_expr_stmt(stmt['value'])
        elif stmt_type == 'pass':
            self._write_line("// pass")
        elif stmt_type == 'break':
            self._write_line("break")
        elif stmt_type == 'continue':
            self._write_line("continue")
        elif stmt_type == 'unsupported':
            self._write_line(f"// Unsupported feature: {stmt.get('feature')}")
        elif stmt_type == 'delete':
            self._write_line("// delete not supported")
        elif stmt_type == 'raise':
            self._generate_raise(stmt)
        elif stmt_type == 'try':
            self._generate_try(stmt)
        elif stmt_type == 'assert':
            self._generate_assert(stmt)
        else:
            self._write_line(f"// Unknown statement type: {stmt_type}")

    def _generate_function(self, func: Dict[str, Any]):
        name = func['name']
        args = func.get('args', [])
        returns = func.get('returns')

        # Build signature
        arg_parts = []
        for arg in args:
            arg_name = arg['name']
            # Try to get a Go type
            go_type = "interface{}"
            if arg.get('type'):
                # Might be an expression representing a type name or complex type
                go_type = self._expr_to_go_type(arg['type'])
            else:
                # Unannotated args in Python are typeless; we could try to infer from usage, but default to interface{}
                pass
            arg_parts.append(f"{arg_name} {go_type}")

        sig = f"func {name}(" + ", ".join(arg_parts) + ")"
        if returns:
            ret_type = self._expr_to_go_type(returns)
            sig += f" {ret_type}"
        self._write_line(sig)
        self._write_line("{")
        self.indent_level += 1

        # Function body: we need a new scope for variables
        saved_vars = self.known_vars.copy()
        self.known_vars = {}
        for stmt in func.get('body', []):
            self._generate_stmt(stmt)
        self.known_vars = saved_vars

        self.indent_level -= 1
        self._write_line("}")

    def _generate_class(self, cls: Dict[str, Any]):
        name = cls['name']
        self._write_line(f"type {name} struct {{")
        self.indent_level += 1
        # Determine fields from __init__ method? Or look for assignments to self.xxx in body.
        # For now, we'll just output a comment and maybe parse assignments to self.
        # We'll scan body for assignments where target is attribute of self.
        for stmt in cls.get('body', []):
            if stmt.get('type') == 'assign':
                targets = stmt['targets']
                # Check if target is attribute with value 'self' or 'this'? In Python it's self.
                if len(targets) == 1:
                    t = targets[0]
                    if t.get('type') == 'attribute' and t['value'].get('type') == 'name' and t['value']['id'] == 'self':
                        field_name = t['attr']
                        value_type = self._infer_type_from_expr(stmt['value'])
                        self._write_line(f"{field_name} {value_type}")
        self.indent_level -= 1
        self._write_line("}")

        # Methods inside class
        for stmt in cls.get('body', []):
            if stmt.get('type') == 'function':
                # Method has a receiver? We need to handle self parameter.
                # In Python, method first arg is self. We'll convert to Go method with pointer receiver if methods modify.
                # Simplify: use value receiver.
                self._generate_method(stmt, cls_name=name)

    def _generate_method(self, func: Dict[str, Any], cls_name: str):
        # func is like a regular function but first argument is self; we'll drop it and make it a method.
        args = func.get('args', [])
        method_name = func['name']
        # Skip first arg (self) for method signature
        if args and args[0]['name'] == 'self':
            args = args[1:]
        arg_parts = []
        for arg in args:
            arg_name = arg['name']
            go_type = "interface{}"
            if arg.get('type'):
                go_type = self._expr_to_go_type(arg['type'])
            arg_parts.append(f"{arg_name} {go_type}")
        sig = f"func (c *{cls_name}) {method_name}(" + ", ".join(arg_parts) + ")"
        returns = func.get('returns')
        if returns:
            ret_type = self._expr_to_go_type(returns)
            sig += " " + ret_type
        self._write_line(sig)
        self._write_line("{")
        self.indent_level += 1
        saved_vars = self.known_vars.copy()
        self.known_vars = {}
        # In method, we have c receiver; we might need to handle self -> c.
        for stmt in func.get('body', []):
            self._generate_stmt(stmt)
        self.known_vars = saved_vars
        self.indent_level -= 1
        self._write_line("}")

    def _generate_assign(self, assign: Dict[str, Any]):
        # Multiple targets allowed in Python. We'll handle one target for simplicity.
        targets = assign['targets']
        value = assign['value']
        value_go_type = self._infer_type_from_expr(value)
        # For now, handle single target assignment.
        if len(targets) == 1:
            target = targets[0]
            if target.get('type') == 'name':
                var_name = target['id']
                # Declare as var or := depending on whether var already known
                if var_name in self.known_vars:
                    # Reassign
                    var_decl = f"{var_name} = "
                else:
                    # New var: use := for short variable declaration
                    var_decl = f"{var_name} := "
                    # If we know value type, we could also explicitly type it; but := infers.
                    # We'll add to known vars
                    self.known_vars[var_name] = value_go_type or "interface{}"
                self._write_line(var_decl + self._expr(value))
            elif target.get('type') == 'attribute':
                # e.g., self.x = value
                base = self._expr(target['value'])
                attr = target['attr']
                self._write_line(f"{base}.{attr} = {self._expr(value)}")
            elif target.get('type') == 'subscript':
                # indexing assignment
                base = self._expr(target['value'])
                index = self._expr(target['slice'])
                self._write_line(f"{base}[{index}] = {self._expr(value)}")
            else:
                self._write_line(f"// Unsupported assignment target: {target.get('type')}")
        else:
            # Multiple assignment: tuple unpacking, etc.
            self._write_line("// Multiple assignment not fully supported")

    def _generate_aug_assign(self, aug: Dict[str, Any]):
        target = self._expr(aug['target'])
        op = operator_to_go(aug['op'])
        value = self._expr(aug['value'])
        self._write_line(f"{target} {op}= {value}")

    def _generate_if(self, if_stmt: Dict[str, Any]):
        test = self._expr(if_stmt['test'])
        self._write_line(f"if {test} {{")
        self.indent_level += 1
        for stmt in if_stmt.get('body', []):
            self._generate_stmt(stmt)
        self.indent_level -= 1
        if if_stmt.get('orelse'):
            self._write_line("} else {")
            self.indent_level += 1
            for stmt in if_stmt['orelse']:
                self._generate_stmt(stmt)
            self.indent_level -= 1
        self._write_line("}")

    def _generate_for(self, for_stmt: Dict[str, Any]):
        # Python: for var in iterable: ...
        target = self._expr(for_stmt['target'])
        iter_expr = self._expr(for_stmt['iter'])
        # If iter is a range call, we can produce Go for with numeric range
        if iter_expr.startswith("range("):
            # Could be range(n) or range(start, stop) or range with step. For simplicity:
            # we assume range(n) -> i from 0 to n-1, or range(a,b) -> i from a to b-1.
            # Remove "range(" and ")".
            inner = iter_expr[6:-1]
            parts = [p.strip() for p in inner.split(',')]
            if len(parts) == 1:
                start = "0"
                end = parts[0]
                step = "1"
            elif len(parts) == 2:
                start, end = parts
                step = "1"
            else:
                start, end, step = parts
            # If target is a single name, use that.
            # If target is a tuple (like idx, val), we need to handle range with index and value.
            # Determine if target is name or tuple.
            if target.startswith("(") and target.endswith(")"):
                # tuple unpacking: (i, v) -> we need two variables
                # simplistically, we can't handle that easily; fall back.
                self._write_line(f"// for loop with tuple unpacking")
                self._write_line("// not fully supported")
                return
            # Go for
            self._write_line(f"for {target} := {start}; {target} < {end}; {target} += {step} {{")
            self.indent_level += 1
            for stmt in for_stmt.get('body', []):
                self._generate_stmt(stmt)
            self.indent_level -= 1
            self._write_line("}")
            return
        # General for loop using range over iterable
        self._write_line(f"for _, {target} := range {iter_expr} {{")
        self.indent_level += 1
        for stmt in for_stmt.get('body', []):
            self._generate_stmt(stmt)
        self.indent_level -= 1
        self._write_line("}")

    def _generate_while(self, while_stmt: Dict[str, Any]):
        test = self._expr(while_stmt['test'])
        self._write_line(f"while {test} {{")
        self.indent_level += 1
        for stmt in while_stmt.get('body', []):
            self._generate_stmt(stmt)
        self.indent_level -= 1
        self._write_line("}")

    def _generate_return(self, ret: Dict[str, Any]):
        value = ret.get('value')
        if value:
            self._write_line("return " + self._expr(value))
        else:
            self._write_line("return")

    def _generate_expr_stmt(self, expr: Dict[str, Any]):
        self._write_line(self._expr(expr))
        # If it's a call, we may need to handle ignoring result?
        # In Go, if we call a function and ignore result, it's fine if no result.
        # If there's a result and we ignore, no issue; but if we need to discard, use _.
        # We'll just output the expression as a statement.

    def _generate_raise(self, raise_stmt: Dict[str, Any]):
        exc = raise_stmt.get('exc')
        if exc:
            self._write_line(f"panic({self._expr(exc)})")
        else:
            self._write_line("panic(\"error\")")

    def _generate_try(self, try_stmt: Dict[str, Any]):
        # In Go, we use defer recover or manual error handling. For now, output comment.
        self._write_line("// try/except block not automatically converted; manual error handling needed")
        # Translate body as if no exception
        for stmt in try_stmt.get('body', []):
            self._generate_stmt(stmt)

    def _generate_assert(self, assert_stmt: Dict[str, Any]):
        test = self._expr(assert_stmt['test'])
        msg = assert_stmt.get('msg')
        if msg:
            self._write_line(f"if !{test} {{ panic({self._expr(msg)}) }}")
        else:
            self._write_line(f"if !{test} {{ panic(\"assertion failed\") }}")

    def _expr(self, expr: Dict[str, Any]) -> str:
        """Convert expression IR to Go code."""
        if not expr:
            return ""
        etype = expr.get('type')
        if etype == 'name':
            return expr['id']
        if etype == 'constant':
            val = expr['value']
            if val is None:
                return "nil"
            if isinstance(val, bool):
                return "true" if val else "false"
            if isinstance(val, str):
                # Escape Go string
                escaped = val.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            if isinstance(val, bytes):
                # bytes literal: e.g., []byte{...} or string conversion
                # For simplicity, use a string cast
                escaped = val.decode('utf-8', 'ignore').replace('\\', '\\\\').replace('"', '\\"')
                return f'[]byte("{escaped}")'
            if val == ...:
                return "..."
            # int, float
            return str(val)
        if etype == 'call':
            func = self._expr(expr['func'])
            args = [self._expr(a) for a in expr.get('args', [])]
            # Map built-in functions
            builtin = builtin_to_go(func.lower() if isinstance(func, str) else None)
            if builtin:
                # Some builtins may have different arg patterns
                if builtin == "len":
                    # len(x) -> len(x)
                    return f"len({args[0]})" if args else "len(?)"
                elif builtin == "range":
                    # range(x) -> range(x) but in Go it's range over something.
                    # We'll just keep "range(x)" and let generator handle for loop.
                    return f"range({', '.join(args)})"
                else:
                    return f"{builtin}({', '.join(args)})"
            # For other functions, use as is, but translate some known ones:
            if func == "print":
                # print(...) -> fmt.Println(...)
                return f"fmt.Println({', '.join(args)})"
            # Default: func(args)
            return f"{func}({', '.join(args)})"
        if etype == 'attribute':
            base = self._expr(expr['value'])
            return f"{base}.{expr['attr']}"
        if etype == 'binop':
            left = self._expr(expr['left'])
            right = self._expr(expr['right'])
            op = operator_to_go(expr['op'])
            return f"({left} {op} {right})"
        if etype == 'unaryop':
            op = operator_to_go(expr['op'])
            operand = self._expr(expr['operand'])
            return f"{op}{operand}"
        if etype == 'compare':
            # Multiple comparisons (a < b < c) are chained. In Go, need && chain.
            left = self._expr(expr['left'])
            comps = []
            for op, comp in zip(expr['ops'], expr['comparators']):
                right = self._expr(comp)
                op_go = operator_to_go(op)
                comps.append(f"{left} {op_go} {right}")
                left = right  # for chain
            if len(comps) == 1:
                return comps[0]
            else:
                return "(" + " && ".join(comps) + ")"
        if etype == 'boolop':
            op = operator_to_go(expr['op'])
            vals = [self._expr(v) for v in expr['values']]
            return f" {op} ".join(vals)
        if etype == 'list':
            elts = [self._expr(e) for e in expr['elts']]
            if not elts:
                return "[]interface{}{}"
            # Infer element type from first element
            first = expr['elts'][0]
            inner_type = self._infer_type_from_expr(first)
            if inner_type and all(self._infer_type_from_expr(e) == inner_type for e in expr['elts']):
                return f"[]{inner_type}{{{', '.join(elts)}}}"
            else:
                return "[]interface{}{" + ", ".join(elts) + "}"
        if etype == 'tuple':
            elts = [self._expr(e) for e in expr['elts']]
            # In Go, tuples become multiple return values or structs. For expressions, we can't directly.
            # Use a helper or just comment.
            return "/* tuple */(" + ", ".join(elts) + ")"
        if etype == 'dict':
            if not expr['keys']:
                return "map[string]interface{}{}"
            # Determine key and value types from first entry
            key_type = self._infer_type_from_expr(expr['keys'][0]) if expr['keys'] else "interface{}"
            val_type = self._infer_type_from_expr(expr['values'][0]) if expr['values'] else "interface{}"
            pairs = []
            for k, v in zip(expr['keys'], expr['values']):
                pairs.append(f"{self._expr(k)}: {self._expr(v)}")
            return f"map[{key_type}]{val_type}{{{', '.join(pairs)}}}"
        if etype == 'subscript':
            base = self._expr(expr['value'])
            index = self._expr(expr['slice'])
            return f"{base}[{index}]"
        if etype == 'lambda':
            args = [arg['name'] for arg in expr.get('args', [])]
            body = self._expr(expr['body'])
            # Go: func(arg) type { return body }
            # We need to infer lambda return type. Hard.
            return f"func({', '.join(args)}) {{ return {body} }}"
        if etype == 'unsupported':
            return f"/* Unsupported: {expr.get('feature')} */"
        # fallback
        return f"/* unknown expr: {etype} */"

    def _infer_type_from_expr(self, expr: Dict[str, Any]) -> str:
        # Use type_mapper
        return infer_type(expr) or "interface{}"

    def _expr_to_go_type(self, expr: Dict[str, Any]) -> str:
        # If expr is a name (like 'int'), return mapped Go type
        if expr.get('type') == 'name':
            name = expr['id']
            return map_python_type_to_go(name) if name in ('int', 'float', 'str', 'bool', 'list', 'dict') else name
        # If it's a constant type? Not likely.
        # If it's a complex type like List[int], we could infer.
        # For now, just use inference
        return self._infer_type_from_expr(expr)

    def _write_line(self, line: str):
        indent = "\t" * self.indent_level
        self.output_lines.append(indent + line)