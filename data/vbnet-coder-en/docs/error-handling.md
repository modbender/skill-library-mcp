# EXCEPTION HANDLING AND RESOURCE MANAGEMENT

> Back to [SKILL.md](../SKILL.md)

---

## Try/Catch/Finally Structure

```vb
' ✓ CORRECT - specific to general exception order
Public Function ProcessFile(path As String) As Boolean
    Try
        Using reader As New StreamReader(path)
            Dim content = reader.ReadToEnd()
            ProcessContent(content)
            Return True
        End Using
    Catch ex As FileNotFoundException
        _logger.LogWarning("File not found: {Path}", path)
        Return False
    Catch ex As IOException
        _logger.LogError(ex, "I/O error reading file: {Path}", path)
        Return False
    Catch ex As UnauthorizedAccessException
        _logger.LogError(ex, "Access denied: {Path}", path)
        Throw New SecurityException("Cannot access file", ex)
    Catch ex As Exception
        _logger.LogCritical(ex, "Unexpected error processing file: {Path}", path)
        Throw
    Finally
        ' Cleanup code - always runs
        CleanupTempFiles()
    End Try
End Function
```

## Exception Best Practices

**DO throw exceptions for exceptional conditions**:
```vb
Public Function Divide(numerator As Integer, denominator As Integer) As Double
    If denominator = 0 Then
        Throw New ArgumentException("Denominator cannot be zero", NameOf(denominator))
    End If
    Return numerator / denominator
End Function
```

**DON'T catch and ignore**:
```vb
' ✗ WRONG - swallowing exceptions
Try
    RiskyOperation()
Catch ex As Exception
    ' Ignored - BAD!
End Try

' ✓ CORRECT - log and rethrow or handle
Try
    RiskyOperation()
Catch ex As Exception
    _logger.LogError(ex, "Operation failed")
    Throw  ' Preserves stack trace
End Try
```

**DO use When clause for filtered exceptions**:
```vb
Try
    Dim result = ProcessData()
Catch ex As InvalidOperationException When ex.Message.Contains("timeout")
    RetryOperation()
Catch ex As InvalidOperationException
    LogAndAbort()
End Try
```

**DO create custom exceptions for domain errors**:
```vb
Public Class CustomerNotFoundException
    Inherits Exception

    Public ReadOnly Property CustomerId As Integer

    Public Sub New(customerId As Integer)
        MyBase.New($"Customer with ID {customerId} was not found")
        Me.CustomerId = customerId
    End Sub

    Public Sub New(customerId As Integer, innerException As Exception)
        MyBase.New($"Customer with ID {customerId} was not found", innerException)
        Me.CustomerId = customerId
    End Sub
End Class
```

---

## IDISPOSABLE AND RESOURCE MANAGEMENT

### Using Statement (Critical)

**ALWAYS use Using for IDisposable objects**:

```vb
' ✓ CORRECT - Using ensures Dispose called even on exception
Using connection As New SqlConnection(connectionString)
    connection.Open()
    Using command As New SqlCommand("SELECT * FROM Users", connection)
        Using reader = command.ExecuteReader()
            While reader.Read()
                ProcessRow(reader)
            End While
        End Using
    End Using
End Using

' ✓ CORRECT - Multiple disposables in one Using
Using connection As New SqlConnection(connectionString), _
      command As New SqlCommand("SELECT * FROM Users", connection)
    connection.Open()
    Dim result = command.ExecuteScalar()
End Using

' ✗ WRONG - manual Dispose (doesn't handle exceptions)
Dim connection As New SqlConnection(connectionString)
connection.Open()
' ... use connection ...
connection.Dispose()  ' Won't execute if exception thrown above
```

### Implementing IDisposable

```vb
Public Class DatabaseRepository
    Implements IDisposable

    Private _connection As SqlConnection
    Private _disposed As Boolean = False

    Public Sub New(connectionString As String)
        _connection = New SqlConnection(connectionString)
    End Sub

    ' Public Dispose method
    Public Sub Dispose() Implements IDisposable.Dispose
        Dispose(True)
        GC.SuppressFinalize(Me)
    End Sub

    ' Protected virtual Dispose pattern
    Protected Overridable Sub Dispose(disposing As Boolean)
        If Not _disposed Then
            If disposing Then
                ' Dispose managed resources
                If _connection IsNot Nothing Then
                    _connection.Dispose()
                    _connection = Nothing
                End If
            End If

            ' Free unmanaged resources here if any

            _disposed = True
        End If
    End Sub

    ' Finalizer (only if unmanaged resources exist)
    ' Protected Overrides Sub Finalize()
    '     Dispose(False)
    '     MyBase.Finalize()
    ' End Sub

    ' Check disposed state in methods
    Private Sub CheckDisposed()
        If _disposed Then
            Throw New ObjectDisposedException(GetType(DatabaseRepository).FullName)
        End If
    End Sub

    Public Function ExecuteQuery(sql As String) As DataTable
        CheckDisposed()
        ' ... implementation
    End Function
End Class
```
