# CLASS AND INTERFACE DESIGN / COMMON PATTERNS

> Back to [SKILL.md](../SKILL.md)

---

## CLASS AND INTERFACE DESIGN

### Property Patterns

```vb
' Auto-implemented properties (preferred)
Public Property Name As String
Public Property IsActive As Boolean
Public Property CreatedDate As Date

' Property with backing field (when logic needed)
Private _age As Integer
Public Property Age As Integer
    Get
        Return _age
    End Get
    Set(value As Integer)
        If value < 0 OrElse value > 150 Then
            Throw New ArgumentOutOfRangeException(NameOf(value))
        End If
        _age = value
    End Set
End Property

' ReadOnly property
Public ReadOnly Property FullName As String
    Get
        Return $"{FirstName} {LastName}"
    End Get
End Property

' ReadOnly auto-property (.NET 4.6+)
Public ReadOnly Property Id As Guid = Guid.NewGuid()

' Property initialization with value
Public Property MaxRetries As Integer = 3
```

### Constructor Patterns

```vb
Public Class Customer
    ' Primary constructor
    Public Sub New(name As String, email As String)
        If String.IsNullOrWhiteSpace(name) Then
            Throw New ArgumentException("Name cannot be empty", NameOf(name))
        End If

        Me.Name = name
        Me.Email = email
        Me.CreatedDate = Date.UtcNow
    End Sub

    ' Parameterless constructor
    Public Sub New()
        Me.New("Unknown", "")
    End Sub

    Public Property Name As String
    Public Property Email As String
    Public Property CreatedDate As Date
End Class
```

### Interface Implementation

```vb
Public Interface IRepository(Of T)
    Function GetByIdAsync(id As Integer) As Task(Of T)
    Function GetAllAsync() As Task(Of IEnumerable(Of T))
    Function AddAsync(entity As T) As Task
    Function UpdateAsync(entity As T) As Task
    Function DeleteAsync(id As Integer) As Task
End Interface

Public Class CustomerRepository
    Implements IRepository(Of Customer)

    Public Async Function GetByIdAsync(id As Integer) As Task(Of Customer) _
        Implements IRepository(Of Customer).GetByIdAsync
        ' Implementation
    End Function

    ' ... other interface members
End Class
```

---

## COMMON PATTERNS

### Factory Pattern

```vb
Public Class CustomerFactory
    Public Shared Function CreateCustomer(type As CustomerType) As Customer
        Select Case type
            Case CustomerType.Premium
                Return New PremiumCustomer()
            Case CustomerType.Standard
                Return New StandardCustomer()
            Case Else
                Throw New ArgumentException("Invalid customer type")
        End Select
    End Function
End Class
```

### Repository Pattern

```vb
Public Class GenericRepository(Of T As Class)
    Implements IRepository(Of T)

    Private ReadOnly _context As DbContext
    Private ReadOnly _dbSet As DbSet(Of T)

    Public Sub New(context As DbContext)
        _context = context
        _dbSet = context.Set(Of T)()
    End Sub

    Public Async Function GetAllAsync() As Task(Of IEnumerable(Of T)) _
        Implements IRepository(Of T).GetAllAsync
        Return Await _dbSet.ToListAsync()
    End Function
End Class
```

### Null Object Pattern

```vb
Public Class NullLogger
    Implements ILogger

    Public Sub LogError(message As String) Implements ILogger.LogError
        ' Do nothing
    End Sub

    Public Sub LogInfo(message As String) Implements ILogger.LogInfo
        ' Do nothing
    End Sub
End Class
```
