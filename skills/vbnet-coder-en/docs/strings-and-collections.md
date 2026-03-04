# STRING HANDLING AND COLLECTIONS

> Back to [SKILL.md](../SKILL.md)

---

## STRING HANDLING

### String Comparison

```vb
' ✓ ALWAYS use StringComparison for culture-aware comparisons
If name.Equals("admin", StringComparison.OrdinalIgnoreCase) Then
    GrantAccess()
End If

' String operations with culture
If name.StartsWith("Mr", StringComparison.CurrentCulture) Then
If name.EndsWith(".txt", StringComparison.OrdinalIgnoreCase) Then
Dim index = text.IndexOf("keyword", StringComparison.Ordinal)

' ✗ WRONG - culture-dependent, unpredictable
If name = "admin" Then  ' Uses default comparison
If name.ToLower() = "admin" Then  ' Unnecessary allocation, culture issues
```

### String Building

```vb
' ✓ Use StringBuilder for multiple concatenations
Dim sb As New StringBuilder()
For Each item In items
    sb.AppendLine($"Item: {item.Name}, Price: {item.Price:C}")
Next
Dim result = sb.ToString()

' ✓ String interpolation for simple formatting
Dim message = $"Customer {customer.Name} ordered {order.ItemCount} items totaling {order.Total:C}"

' ✗ AVOID - repeated concatenation in loops (O(n²) performance)
Dim result = ""
For Each item In items
    result &= item.ToString() & vbCrLf  ' Creates new string each iteration
Next
```

### String Constants

```vb
' Use standard VB.NET constants
Dim lines = text.Split({vbCrLf, vbLf}, StringSplitOptions.RemoveEmptyEntries)
Dim path = folder & vbBack & filename  ' Backslash
Dim message = "Line 1" & vbNewLine & "Line 2"  ' Platform-specific newline
```

---

## COLLECTIONS AND ARRAYS

### Choosing Collection Types

```vb
' List(Of T) - default choice for most scenarios
Dim customers As New List(Of Customer)
customers.Add(New Customer())
customers.AddRange(moreCustomers)

' Dictionary(Of TKey, TValue) - fast key-based lookup
Dim customerLookup As New Dictionary(Of Integer, Customer)
customerLookup(123) = customer
If customerLookup.ContainsKey(id) Then
    Dim found = customerLookup(id)
End If

' HashSet(Of T) - unique items, fast Contains
Dim uniqueEmails As New HashSet(Of String)(StringComparer.OrdinalIgnoreCase)
uniqueEmails.Add(email)

' Queue(Of T) - FIFO
Dim processingQueue As New Queue(Of Task)
processingQueue.Enqueue(task)
Dim next = processingQueue.Dequeue()

' Stack(Of T) - LIFO
Dim undoStack As New Stack(Of Command)
undoStack.Push(command)
Dim lastCommand = undoStack.Pop()

' ReadOnlyCollection(Of T) - immutable view
Public ReadOnly Property Items As ReadOnlyCollection(Of String)
    Get
        Return New ReadOnlyCollection(Of String)(_items)
    End Get
End Property

' Array - fixed size, performance critical, interop
Dim buffer(1023) As Byte
Dim matrix(,) As Double = New Double(9, 9) {}  ' 2D array
```

### Collection Initialization

```vb
' Collection initializer
Dim numbers As New List(Of Integer) From {1, 2, 3, 4, 5}
Dim customers As New List(Of Customer) From {
    New Customer With {.Name = "John"},
    New Customer With {.Name = "Jane"}
}

' Dictionary initializer
Dim lookup As New Dictionary(Of String, Integer) From {
    {"one", 1},
    {"two", 2},
    {"three", 3}
}

' Array initializer
Dim primes() As Integer = {2, 3, 5, 7, 11, 13}
```
