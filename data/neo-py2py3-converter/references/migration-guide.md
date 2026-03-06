# Python 2 to 3 Migration Guide

## Syntax Changes

### Print Statement
Python 2: `print "hello"`
Python 3: `print("hello")`

The print statement became a function in Python 3. All forms must be converted:
- `print "a", "b"` → `print("a", "b")`
- `print >> sys.stderr, "err"` → `print("err", file=sys.stderr)`
- `print "a",` (trailing comma suppresses newline) → `print("a", end=" ")`

### Exception Handling
Python 2: `except Exception, e:`
Python 3: `except Exception as e:`

### Raise Statement
Python 2: `raise ValueError, "message"`
Python 3: `raise ValueError("message")`

### Integer Division
Python 2: `5 / 2` returns `2` (integer)
Python 3: `5 / 2` returns `2.5` (float)
Use `5 // 2` for integer division in Python 3.

## Built-in Changes

### Removed Built-ins
| Python 2 | Python 3 |
|-----------|-----------|
| `raw_input()` | `input()` |
| `xrange()` | `range()` |
| `unicode()` | `str()` |
| `long` | `int` |
| `reduce()` | `functools.reduce()` |
| `basestring` | `str` |

### Dictionary Methods
| Python 2 | Python 3 |
|-----------|-----------|
| `dict.has_key(k)` | `k in dict` |
| `dict.iteritems()` | `dict.items()` |
| `dict.itervalues()` | `dict.values()` |
| `dict.iterkeys()` | `dict.keys()` |

## Import Changes

| Python 2 | Python 3 |
|-----------|-----------|
| `import urllib2` | `import urllib.request` |
| `import urlparse` | `import urllib.parse` |
| `import ConfigParser` | `import configparser` |
| `import Queue` | `import queue` |
| `import StringIO` | `import io` |
| `import cPickle` | `import pickle` |
| `import HTMLParser` | `import html.parser` |
| `import httplib` | `import http.client` |
| `import thread` | `import _thread` |

## Future Imports
These `__future__` imports are no longer needed in Python 3:
- `from __future__ import print_function`
- `from __future__ import unicode_literals`
- `from __future__ import absolute_import`
- `from __future__ import division`

## 2to3 Tool Limitations
The standard `2to3` tool:
- Does not handle all edge cases
- Cannot convert library-specific patterns
- May produce code that is not idiomatic Python 3
- Does not generate tests for converted code

This skill addresses these limitations by providing more thorough pattern matching and test generation.
