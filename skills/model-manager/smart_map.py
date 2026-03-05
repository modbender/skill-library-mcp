#!/usr/bin/env python3
"""
Cognitive Map Generator - Creates a high-level summary of a Python codebase using AST analysis.
"""

import os
import ast
import sys

class CodebaseMapper:
    def __init__(self):
        self.skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env'}
        self.skip_files = {'.DS_Store'}

    def should_skip(self, name: str) -> bool:
        """Check if a file or directory should be skipped."""
        return name.startswith('.') or name in self.skip_dirs or name in self.skip_files

    def parse_python_file(self, file_path: str) -> list[str]:
        """Parse a Python file and extract its structure as a list of strings."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            return [f"⚠️ Error parsing: {str(e)}"]

        lines = []
        
        # Helper for recursive traversal
        def visit(nodes, level=0):
            prefix = "  " * level
            for node in nodes:
                if isinstance(node, ast.ClassDef):
                    bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                    base_str = f"({', '.join(bases)})" if bases else ""
                    doc = ast.get_docstring(node)
                    doc_summary = f" - \"{doc.splitlines()[0]}\"" if doc else ""
                    lines.append(f"{prefix}📦 class {node.name}{base_str}{doc_summary}")
                    # Recurse into class body
                    visit(node.body, level + 1)
                    
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in node.args.args]
                    # Filter out 'self' for brevity in methods
                    if args and args[0] == 'self':
                        args = args[1:]
                    args_str = ", ".join(args)
                    
                    doc = ast.get_docstring(node)
                    doc_summary = ""
                    # Only show docstring for top-level functions or major methods to save space
                    if doc and level <= 1: 
                        doc_summary = f" - \"{doc.splitlines()[0]}\""
                    
                    icon = "🔹" if level > 0 else "ƒ "
                    lines.append(f"{prefix}{icon}def {node.name}({args_str}){doc_summary}")

        visit(tree.body)
        return lines

    def generate_markdown(self, base_path: str) -> str:
        """Generate a markdown representation of the codebase structure."""
        output = []
        
        for root, dirs, files in os.walk(base_path):
            # Filter dirs in-place
            dirs[:] = [d for d in dirs if not self.should_skip(d)]
            dirs.sort()
            
            # Calculate indentation
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                level = 0
            else:
                level = len(rel_path.split(os.sep))
                # Add directory name
                indent = '  ' * (level - 1)
                output.append(f'{indent}📂 {os.path.basename(root)}/')
            
            indent = '  ' * level
            
            for file in sorted(files):
                if self.should_skip(file):
                    continue
                    
                file_path = os.path.join(root, file)
                
                # Add file name
                output.append(f'{indent}📄 {file}')
                
                # If Python, add AST structure
                if file.endswith('.py'):
                    structure = self.parse_python_file(file_path)
                    for line in structure:
                        output.append(f'{indent}  {line}')
        
        return '\n'.join(output)

def main():
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()
        
    mapper = CodebaseMapper()
    print(f"🗺️ Cognitive Map of: {target_dir}\n")
    print(mapper.generate_markdown(target_dir))

if __name__ == '__main__':
    main()
