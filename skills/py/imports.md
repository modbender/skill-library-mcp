# Import Traps

- Circular import — partially initialized module, `ImportError` or `None` attrs
- `from x import *` — pollutes namespace, shadows builtins
- Relative import outside package — `from . import x` fails in script
- `__init__.py` side effects — runs on ANY import from package
- Import caching — `importlib.reload()` needed for changes, but breaks refs
- Module runs on import — top-level code executes, use `if __name__ == "__main__"`
- `sys.path` modification — affects ALL imports, prefer proper packaging
