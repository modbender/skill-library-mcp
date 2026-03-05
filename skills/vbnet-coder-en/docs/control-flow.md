# CONTROL FLOW

> Back to [SKILL.md](../SKILL.md)

---

## Conditional Statements

**Always use explicit blocks**:

```vb
' ✓ CORRECT - explicit Then/End If
If condition Then
    DoSomething()
End If

If value > 100 Then
    ProcessLarge(value)
ElseIf value > 10 Then
    ProcessMedium(value)
Else
    ProcessSmall(value)
End If

' ✓ CORRECT - single-line for trivial cases only
If x > 0 Then Return True

' ✗ WRONG - multi-statement single-line
If x > 0 Then y = 1 : z = 2
```

## Select Case (Switch)

```vb
' Use Select Case for multiple conditions
Select Case status
    Case OrderStatus.Pending
        ProcessPending()
    Case OrderStatus.Approved, OrderStatus.Processing
        ProcessActive()
    Case OrderStatus.Completed
        CompleteOrder()
    Case Else
        HandleUnknown()
End Select

' Type switch pattern
Select Case True
    Case TypeOf obj Is Customer
        ProcessCustomer(DirectCast(obj, Customer))
    Case TypeOf obj Is Order
        ProcessOrder(DirectCast(obj, Order))
    Case Else
        Throw New ArgumentException()
End Select
```

## Loops

```vb
' For loop - use when count known
For i As Integer = 0 To collection.Count - 1
    Process(collection(i))
Next

' For Each - preferred for enumeration
For Each item As String In collection
    Process(item)
Next

' While loop - condition at start
While reader.Read()
    ProcessRow(reader)
End While

' Do loop - condition at end (executes at least once)
Do
    ProcessBatch()
Loop Until batchComplete

' Exit loops early
For Each item In items
    If item.IsInvalid Then Continue For  ' Skip to next
    If item.IsCritical Then Exit For     ' Exit loop
    Process(item)
Next
```
