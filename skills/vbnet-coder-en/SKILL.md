---
name: VB.NET CODING AGENT SKILL REFERENCE
description: "For detailed patterns, examples, and best practices on specific topics, see:"
---

# VB.NET CODING AGENT SKILL REFERENCE

**Target**: Claude-Code, Codex, AI coding agents
**Version**: 2026 Modern .NET
**Max Lines**: 500

---

## DETAILED REFERENCES

For detailed patterns, examples, and best practices on specific topics, see:

| Topic | File | When to consult |
|-------|------|-----------------|
| Type System | [docs/types-and-declarations.md](docs/types-and-declarations.md) | Variable declarations, nullable types, field declarations |
| Control Flow | [docs/control-flow.md](docs/control-flow.md) | If/ElseIf, Select Case, loops, Exit/Continue |
| Async/Await | [docs/async-patterns.md](docs/async-patterns.md) | Async method structure, ConfigureAwait, cancellation, Task.WhenAll |
| Error Handling | [docs/error-handling.md](docs/error-handling.md) | Exceptions, Try/Catch/Finally, IDisposable, Using statement |
| LINQ | [docs/linq-patterns.md](docs/linq-patterns.md) | Query/method syntax, common operations, deferred execution |
| Strings & Collections | [docs/strings-and-collections.md](docs/strings-and-collections.md) | String comparison/building, List, Dictionary, HashSet, arrays |
| Class Design & Patterns | [docs/class-design-and-patterns.md](docs/class-design-and-patterns.md) | Properties, constructors, interfaces, Factory, Repository, Null Object |

---

## CRITICAL COMPILER DIRECTIVES

### Mandatory File Headers

**ALWAYS include at top of every file:**

```vb
Option Explicit On
Option Strict On
Option Infer On
```

**Rationale**: Option Explicit On prevents undeclared variable usage (catches typos), Option Strict On enforces type safety (prevents implicit conversions causing runtime errors), Option Infer On enables local type inference while maintaining type safety.

**Never use**: `Option Explicit Off` or `Option Strict Off` - these create runtime errors, performance degradation, and late binding overhead.

**Project-level setting preferred**: Set in `.vbproj` file rather than per-file when possible.

---

## NAMING CONVENTIONS

### Core Rules

| Element | Convention | Example |
|---------|-----------|---------|
| **Namespace** | PascalCase, hierarchical | `CompanyName.ProductName.ComponentName` |
| **Class/Interface** | PascalCase, noun/noun phrase | `CustomerRepository`, `IPaymentProcessor` |
| **Interface prefix** | Starts with `I` | `IDisposable`, `IEnumerable(Of T)` |
| **Method** | PascalCase, verb/verb phrase | `CalculateTotal()`, `ProcessPayment()` |
| **Property** | PascalCase, noun/adjective | `CustomerName`, `IsActive` |
| **Field (private)** | _camelCase with underscore | `_connectionString`, `_maxRetries` |
| **Field (public/shared)** | PascalCase | `MaxValue`, `DefaultTimeout` |
| **Parameter/Local** | camelCase | `userId`, `itemCount` |
| **Constant** | PascalCase or UPPER_SNAKE | `MaxConnections`, `DEFAULT_TIMEOUT` |
| **Enum Type** | PascalCase, singular | `OrderStatus`, `FileMode` |
| **Enum Members** | PascalCase | `OrderStatus.Pending`, `FileMode.Read` |
| **Event** | PascalCase, verb phrase | `DataReceived`, `ConnectionClosed` |
| **Delegate** | PascalCase, ends with Handler/Callback | `EventHandler`, `DataReceivedCallback` |
| **Generic Type Param** | T + PascalCase | `TKey`, `TValue`, `TEntity` |

### Specific Guidelines

**Boolean names**: Use `Is`, `Has`, `Can`, `Should` prefixes:
```vb
Dim isValid As Boolean
Dim hasChildren As Boolean
Dim canProcess As Boolean
```

**Collection/Array naming**: Plural nouns:
```vb
Dim customers As List(Of Customer)
Dim orderIds() As Integer
```

**Async method suffix**: Always use `Async`:
```vb
Public Async Function LoadDataAsync() As Task(Of DataSet)
Public Async Function SaveCustomerAsync(customer As Customer) As Task
```

**Avoid**: Hungarian notation (`strName`, `intCount`), `My` prefix (conflicts with VB.NET `My` namespace), abbreviations unless universally known (OK: `Id`, `Xml`, `Http`; Avoid: `Mgr`, `Proc`, `Calc`).

---

## CODE LAYOUT AND STYLE

### Indentation and Spacing

- **4 spaces per indentation level** (never tabs)
- **One statement per line**
- **One blank line** between methods/properties
- **Line continuation**: Use implicit continuation (no underscore) where possible

```vb
' ✓ Implicit line continuation (no underscore needed)
Dim result = customers _
    .Where(Function(c) c.IsActive) _
    .OrderBy(Function(c) c.Name) _
    .ToList()

Dim customer = New Customer With {
    .Name = "John",
    .Email = "john@example.com",
    .IsActive = True
}

' Method parameters
Public Function ProcessOrder(
    orderId As Integer,
    customerId As Integer,
    processDate As Date) As OrderResult
```

### Comments

```vb
' Single-line comment for brief explanations

''' <summary>
''' Processes customer orders asynchronously.
''' </summary>
''' <param name="customerId">The unique customer identifier.</param>
''' <param name="cancellationToken">Token to cancel the operation.</param>
''' <returns>A task representing the async operation with the order result.</returns>
''' <exception cref="CustomerNotFoundException">Thrown when customer not found.</exception>
Public Async Function ProcessOrdersAsync(
    customerId As Integer,
    cancellationToken As CancellationToken) As Task(Of OrderResult)

    ' Implementation
End Function
```

**Avoid**: Commenting obvious code, redundant comments, commented-out code (use version control).

---

## FILE ORGANIZATION

**Standard file structure**:

```vb
Option Explicit On
Option Strict On
Option Infer On

Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Threading.Tasks

Namespace CompanyName.ProjectName.ComponentName

    ''' <summary>
    ''' Brief class description.
    ''' </summary>
    Public Class ClassName
        ' Constants
        Private Const DefaultTimeout As Integer = 30

        ' Shared (static) fields
        Public Shared ReadOnly MaxConnections As Integer = 100

        ' Private fields
        Private _connectionString As String
        Private ReadOnly _logger As ILogger

        ' Constructors
        Public Sub New(logger As ILogger)
            _logger = logger
        End Sub

        ' Properties
        Public Property Name As String

        ' Methods
        Public Function DoSomething() As Integer
            ' Implementation
        End Function

        ' IDisposable implementation if needed
        Public Sub Dispose() Implements IDisposable.Dispose
            ' Cleanup
        End Sub
    End Class
End Namespace
```

---

## PERFORMANCE CONSIDERATIONS

**Avoid boxing/unboxing**: Use generics instead of Object collections.

**String comparisons**: Use `StringComparison.Ordinal` for best performance when culture doesn't matter.

**LINQ materialization**: Call `.ToList()` only when needed; leverage deferred execution.

**Async I/O**: Always use async for file, database, network operations.

**ConfigureAwait(False)**: Use in library code to avoid sync context overhead.

**StringBuilder**: Use for concatenating >3-4 strings in loops.

**Collection capacity**: Set initial capacity for `List(Of T)` and `Dictionary(Of K, V)` when size known.

```vb
Dim customers As New List(Of Customer)(expectedCount)  ' Avoid reallocations
```

---

## COMMON ANTI-PATTERNS TO AVOID

❌ **Option Strict Off** - causes runtime errors, performance issues
❌ **Async void methods** - unobservable exceptions (except event handlers)
❌ **Blocking async code** - `.Result`, `.Wait()` cause deadlocks
❌ **Catching Exception without logging** - swallows errors
❌ **Not disposing IDisposable** - memory/resource leaks
❌ **Using == for strings** - culture-dependent, use `.Equals()` with `StringComparison`
❌ **String concatenation in loops** - O(n²) performance
❌ **Not using Using statement** - resources not released on exception
❌ **Hungarian notation** - outdated, conflicts with modern style
❌ **Magic numbers** - use named constants
❌ **Deep nesting** - extract methods, early returns

---

## AGENT-SPECIFIC GUIDANCE

**When generating VB.NET code:**

1. **Always include** `Option Explicit On` and `Option Strict On` at file top
2. **Use explicit types** for all declarations
3. **Prefer method syntax LINQ** over query syntax (easier for agent parsing)
4. **Always use Using** for IDisposable objects
5. **Use Async/Await** for any I/O operations
6. **Include XML documentation** for public APIs
7. **Use meaningful names** - prioritize readability over brevity
8. **Handle exceptions explicitly** - no empty catches
9. **Follow naming conventions** exactly - PascalCase for public, _camelCase for private fields
10. **One responsibility per method** - extract when logic grows
11. **Prefer composition over inheritance** - use interfaces
12. **Immutability when possible** - ReadOnly fields, ReadOnly properties
13. **Validate parameters** at method entry
14. **Use CancellationToken** for long-running async operations
15. **Log errors with context** - include relevant data in log messages

---

**END OF SKILL REFERENCE**

*This document is optimized for AI coding agents generating modern, maintainable VB.NET code targeting .NET Framework 4.8+ and .NET 6/7/8+*
