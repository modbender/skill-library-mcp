#!/usr/bin/env python3
"""
Python AST parser for extracting function signatures and docstrings.

This module uses Python's ast module to parse source code and extract
structured information about functions and methods, including their
parameters, type hints, and documentation.
"""

import ast
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any


@dataclass
class Parameter:
    """Represents a function parameter."""
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None
    kind: str = "positional_or_keyword"  # positional_only, positional_or_keyword, var_positional, keyword_only, var_keyword

    def is_required(self) -> bool:
        """Check if parameter is required (no default value)."""
        return self.default is None

    def get_type_hint(self) -> str:
        """Get the type hint as a string."""
        return self.annotation if self.annotation else "Any"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "annotation": self.annotation,
            "default": self.default,
            "kind": self.kind,
            "required": self.is_required()
        }


@dataclass
class Function:
    """Represents a parsed function or method."""
    name: str
    parameters: List[Parameter] = field(default_factory=list)
    docstring: Optional[str] = None
    returns: Optional[str] = None
    is_method: bool = False
    class_name: Optional[str] = None
    line_number: int = 0
    decorators: List[str] = field(default_factory=list)

    def get_required_params(self) -> List[Parameter]:
        """Get list of required parameters."""
        return [p for p in self.parameters if p.is_required()]

    def get_optional_params(self) -> List[Parameter]:
        """Get list of optional parameters (with defaults)."""
        return [p for p in self.parameters if not p.is_required()]

    def has_var_positional(self) -> bool:
        """Check if function accepts *args."""
        return any(p.kind == "var_positional" for p in self.parameters)

    def has_var_keyword(self) -> bool:
        """Check if function accepts **kwargs."""
        return any(p.kind == "var_keyword" for p in self.parameters)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "docstring": self.docstring,
            "returns": self.returns,
            "is_method": self.is_method,
            "class_name": self.class_name,
            "line_number": self.line_number,
            "decorators": self.decorators
        }


class PythonParser:
    """
    Parses Python source code to extract function definitions.

    Uses Python's ast module to build an abstract syntax tree and walk
    through it to collect function and method information.
    """

    def __init__(self, source_code: str, filename: str = "<unknown>"):
        """
        Initialize the parser.

        Args:
            source_code: Raw Python source code as a string
            filename: Name of the file (for error reporting)
        """
        self.source_code = source_code
        self.filename = filename
        self.tree = None
        self.functions: List[Function] = []

    def parse(self) -> List[Function]:
        """
        Parse the source code and extract all functions.

        Returns:
            List of Function objects representing all found functions and methods

        Raises:
            SyntaxError: If the source code has invalid Python syntax
        """
        try:
            self.tree = ast.parse(self.source_code, filename=self.filename)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in {self.filename}: {e.msg} at line {e.lineno}")

        self._walk_tree(self.tree)
        return self.functions

    def _walk_tree(self, node: ast.AST, class_name: Optional[str] = None):
        """
        Recursively walk the AST tree to find function definitions.

        Args:
            node: Current AST node
            class_name: Name of enclosing class (if any)
        """
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                self._process_function(child, class_name)
            elif isinstance(child, ast.AsyncFunctionDef):
                self._process_function(child, class_name, is_async=True)
            elif isinstance(child, ast.ClassDef):
                # Recurse into class definitions
                self._walk_tree(child, class_name=child.name)

    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], class_name: Optional[str], is_async: bool = False):
        """
        Extract information from a function definition node.

        Args:
            node: FunctionDef or AsyncFunctionDef AST node
            class_name: Enclosing class name (None for standalone functions)
            is_async: Whether this is an async function
        """
        # Get function name
        func_name = node.name

        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorators.append(decorator.func.id)
            else:
                decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else str(decorator))

        # Parse parameters
        parameters = self._parse_parameters(node)

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get return type annotation
        returns = None
        if node.returns:
            returns = self._format_annotation(node.returns)

        # Create Function object
        function = Function(
            name=func_name,
            parameters=parameters,
            docstring=docstring,
            returns=returns,
            is_method=class_name is not None,
            class_name=class_name,
            line_number=node.lineno,
            decorators=decorators
        )

        self.functions.append(function)

    def _parse_parameters(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> List[Parameter]:
        """
        Extract parameter information from a function node.

        Args:
            node: Function definition node

        Returns:
            List of Parameter objects
        """
        parameters = []

        # Regular arguments (positional or keyword)
        for arg in node.args.args:
            param = Parameter(
                name=arg.arg,
                annotation=self._format_annotation(arg.annotation) if arg.annotation else None,
                kind="positional_or_keyword"
            )
            parameters.append(param)

        # Positional-only arguments (Python 3.8+)
        if hasattr(node.args, 'posonlyargs'):
            for arg in node.args.posonlyargs:
                param = Parameter(
                    name=arg.arg,
                    annotation=self._format_annotation(arg.annotation) if arg.annotation else None,
                    kind="positional_only"
                )
                parameters.append(param)

        # *args
        if node.args.vararg:
            param = Parameter(
                name=node.args.vararg.arg,
                annotation=self._format_annotation(node.args.vararg.annotation) if node.args.vararg.annotation else None,
                kind="var_positional"
            )
            parameters.append(param)

        # Keyword-only arguments
        for arg in node.args.kwonlyargs:
            param = Parameter(
                name=arg.arg,
                annotation=self._format_annotation(arg.annotation) if arg.annotation else None,
                kind="keyword_only"
            )
            parameters.append(param)

        # **kwargs
        if node.args.kwarg:
            param = Parameter(
                name=node.args.kwarg.arg,
                annotation=self._format_annotation(node.args.kwarg.annotation) if node.args.kwarg.annotation else None,
                kind="var_keyword"
            )
            parameters.append(param)

        # Extract default values (they align with the last N positional/keyword parameters)
        defaults = node.args.defaults
        num_positional_params = len(node.args.args) + (len(node.args.posonlyargs) if hasattr(node.args, 'posonlyargs') else 0)
        num_defaults = len(defaults)

        # Defaults are applied to the last N parameters
        default_start_index = num_positional_params - num_defaults
        for i, default in enumerate(defaults):
            param_index = default_start_index + i
            if param_index < len(parameters):
                parameters[param_index].default = self._format_default(default)

        # Keyword-only defaults
        kwdefaults = node.args.kw_defaults
        kwonly_start = num_positional_params
        for i, default in enumerate(kwdefaults):
            if default:
                param_index = kwonly_start + i
                if param_index < len(parameters):
                    parameters[param_index].default = self._format_default(default)

        return parameters

    def _format_annotation(self, annotation: ast.AST) -> str:
        """
        Format a type annotation AST node as a string.

        Args:
            annotation: AST node representing the type annotation

        Returns:
            String representation of the annotation
        """
        if hasattr(ast, 'unparse'):
            return ast.unparse(annotation)
        else:
            # Fallback for older Python versions - basic representation
            return self._simple_annotation_str(annotation)

    def _simple_annotation_str(self, node: ast.AST) -> str:
        """Simple annotation string representation (fallback)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self._simple_annotation_str(node.value)
            slice_str = self._simple_annotation_str(node.slice)
            return f"{value}[{slice_str}]"
        elif isinstance(node, ast.Tuple):
            elts = [self._simple_annotation_str(elt) for elt in node.elts]
            return ", ".join(elts)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "Any"

    def _format_default(self, default: ast.AST) -> str:
        """
        Format a default value AST node as a string.

        Args:
            default: AST node representing the default value

        Returns:
            String representation of the default value
        """
        if hasattr(ast, 'unparse'):
            return ast.unparse(default)
        else:
            # Fallback for common constants
            if isinstance(default, ast.Constant):
                return repr(default.value)
            elif isinstance(default, ast.Name):
                return default.id
            elif isinstance(default, ast.NameConstant):  # Python < 3.8
                return repr(default.value)
            else:
                return "..."
