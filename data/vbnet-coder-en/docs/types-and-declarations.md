# TYPE SYSTEM AND DECLARATIONS

> Back to [SKILL.md](../SKILL.md)

---

## Variable Declaration

**Always explicit types** (Option Strict On enforced):

```vb
' ✓ CORRECT - explicit types
Dim count As Integer = 0
Dim name As String = "Default"
Dim customer As Customer = Nothing
Dim items As New List(Of String)

' ✓ CORRECT - type inference allowed (Option Infer On)
Dim implicitNumber = 42           ' Integer
Dim implicitString = "Hello"      ' String
Dim implicitList = New List(Of Integer)()

' ✗ WRONG - requires Option Strict Off
Dim x                             ' Object type, slow
Dim y = Nothing                   ' Object type
```

## Multiple Declarations

**One declaration per line** (debugger friendly):

```vb
' ✓ CORRECT
Dim firstName As String
Dim lastName As String
Dim age As Integer

' ✗ WRONG - hard to debug, step through
Dim firstName As String, lastName As String, age As Integer
```

## Field Declarations

```vb
Public Class Repository
    ' Private field with underscore prefix
    Private _connectionString As String
    Private _maxRetries As Integer = 3

    ' Public shared (static) field
    Public Shared ReadOnly DefaultTimeout As Integer = 30

    ' Constant
    Private Const MaxBufferSize As Integer = 8192

    ' ReadOnly field (immutable after constructor)
    Private ReadOnly _logger As ILogger

    Public Sub New(logger As ILogger)
        _logger = logger
    End Sub
End Class
```

## Nullable Types

```vb
' Nullable value types (modern syntax .NET 4.0+)
Dim nullableInt As Integer? = Nothing
Dim nullableDate As Date?

' Check for null
If nullableInt.HasValue Then
    Console.WriteLine(nullableInt.Value)
End If

' Null coalescing
Dim result As Integer = nullableInt.GetValueOrDefault(0)

' Reference types are nullable by default in VB.NET
Dim customer As Customer = Nothing
```
