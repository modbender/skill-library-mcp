# ASYNC/AWAIT PATTERNS

> Back to [SKILL.md](../SKILL.md)

---

## Core Principles

**Always use Async/Await for I/O operations**: File, network, database, HTTP calls.

**Naming**: Suffix async methods with `Async`.

**Return types**: `Task`, `Task(Of T)`, or `ValueTask(Of T)` for performance-critical code.

## Async Method Structure

```vb
' ✓ CORRECT - async method pattern
Public Async Function LoadCustomerAsync(id As Integer) As Task(Of Customer)
    Try
        Using connection As New SqlConnection(_connectionString)
            Await connection.OpenAsync()
            Using command As New SqlCommand("SELECT * FROM Customers WHERE Id = @Id", connection)
                command.Parameters.AddWithValue("@Id", id)
                Using reader = Await command.ExecuteReaderAsync()
                    If Await reader.ReadAsync() Then
                        Return MapCustomer(reader)
                    End If
                End Using
            End Using
        End Using
    Catch ex As SqlException
        _logger.LogError(ex, "Database error loading customer {CustomerId}", id)
        Throw New DataAccessException("Failed to load customer", ex)
    Catch ex As Exception
        _logger.LogError(ex, "Unexpected error loading customer {CustomerId}", id)
        Throw
    End Try

    Return Nothing
End Function

' ✓ CORRECT - Task without result
Public Async Function SaveCustomerAsync(customer As Customer) As Task
    Await _repository.SaveAsync(customer)
    Await _cache.InvalidateAsync(customer.Id)
End Function

' ✗ WRONG - async void (only for event handlers)
Public Async Sub LoadDataAsync()  ' DON'T DO THIS
    Await LoadAsync()
End Sub
```

## Exception Handling in Async

```vb
' Try/Catch works naturally with Await
Public Async Function ProcessAsync() As Task(Of Result)
    Try
        Dim data = Await FetchDataAsync()
        Dim processed = Await ProcessDataAsync(data)
        Return processed
    Catch ex As HttpRequestException
        ' Handle specific exception
        _logger.LogWarning(ex, "HTTP error during processing")
        Return Result.Failed("Network error")
    Catch ex As OperationCanceledException
        ' Handle cancellation
        _logger.LogInformation("Operation cancelled")
        Return Result.Cancelled()
    Catch ex As Exception
        ' Handle unexpected
        _logger.LogError(ex, "Unexpected error during processing")
        Throw New ProcessingException("Failed to process data", ex)
    End Try
End Function
```

## ConfigureAwait Pattern

```vb
' Library code - use ConfigureAwait(False) to avoid capturing sync context
Public Async Function GetDataAsync() As Task(Of String)
    Using client As New HttpClient()
        Dim response = Await client.GetAsync(url).ConfigureAwait(False)
        Return Await response.Content.ReadAsStringAsync().ConfigureAwait(False)
    End Using
End Function

' UI code - omit ConfigureAwait or use ConfigureAwait(True) to return to UI thread
Private Async Sub Button_Click(sender As Object, e As EventArgs)
    Dim data = Await LoadDataAsync()  ' Returns to UI thread
    textBox.Text = data
End Sub
```

## Async Best Practices

```vb
' ✓ Use Task.WhenAll for parallel operations
Dim customerTask = LoadCustomerAsync(id)
Dim ordersTask = LoadOrdersAsync(id)
Dim invoicesTask = LoadInvoicesAsync(id)
Await Task.WhenAll(customerTask, ordersTask, invoicesTask)

Dim customer = Await customerTask
Dim orders = Await ordersTask
Dim invoices = Await invoicesTask

' ✓ Use CancellationToken for cancellable operations
Public Async Function LoadDataAsync(cancellationToken As CancellationToken) As Task(Of Data)
    cancellationToken.ThrowIfCancellationRequested()

    Dim data = Await _client.GetAsync(url, cancellationToken)

    ' Check cancellation in long loops
    For Each item In largeCollection
        cancellationToken.ThrowIfCancellationRequested()
        Await ProcessAsync(item)
    Next

    Return data
End Function

' ✗ AVOID - blocking on async code (causes deadlocks)
Dim result = LoadDataAsync().Result        ' DEADLOCK RISK
Dim data = LoadDataAsync().GetAwaiter().GetResult()  ' DEADLOCK RISK
```
