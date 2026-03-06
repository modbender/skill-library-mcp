# LINQ PATTERNS

> Back to [SKILL.md](../SKILL.md)

---

## Query Syntax vs Method Syntax

```vb
' Query syntax - readable for complex queries
Dim expensiveOrders = From order In orders
                      Where order.Total > 1000
                      Order By order.Date Descending
                      Select order

' Method syntax - preferred by AI agents (chainable, IntelliSense friendly)
Dim expensiveOrders = orders _
    .Where(Function(o) o.Total > 1000) _
    .OrderByDescending(Function(o) o.Date) _
    .ToList()

' Mixing both
Dim result = From customer In customers
             Where customer.IsActive
             Select New With {
                 .Name = customer.Name,
                 .OrderCount = customer.Orders.Count(Function(o) o.Year = 2026)
             }
```

## Common LINQ Operations

```vb
' Filtering
Dim activeCustomers = customers.Where(Function(c) c.IsActive).ToList()

' Projection
Dim customerNames = customers.Select(Function(c) c.Name).ToList()
Dim dto = customers.Select(Function(c) New CustomerDto With {
    .Id = c.Id,
    .Name = c.Name
}).ToList()

' Ordering
Dim sorted = orders.OrderBy(Function(o) o.Date).ThenByDescending(Function(o) o.Total)

' Aggregation
Dim totalRevenue = orders.Sum(Function(o) o.Total)
Dim avgOrderValue = orders.Average(Function(o) o.Total)
Dim maxOrder = orders.Max(Function(o) o.Total)
Dim orderCount = orders.Count(Function(o) o.Status = OrderStatus.Completed)

' Grouping
Dim groupedByYear = orders.GroupBy(Function(o) o.Date.Year) _
    .Select(Function(g) New With {
        .Year = g.Key,
        .Orders = g.ToList(),
        .Total = g.Sum(Function(o) o.Total)
    }).ToList()

' Joining
Dim result = customers _
    .Join(orders,
          Function(c) c.Id,
          Function(o) o.CustomerId,
          Function(c, o) New With {.CustomerName = c.Name, .OrderTotal = o.Total})

' Any/All
Dim hasActiveOrders = customer.Orders.Any(Function(o) o.IsActive)
Dim allCompleted = customer.Orders.All(Function(o) o.Status = OrderStatus.Completed)

' FirstOrDefault/SingleOrDefault (avoid exceptions)
Dim firstActive = customers.FirstOrDefault(Function(c) c.IsActive)  ' Returns Nothing if not found
Dim singleMatch = customers.SingleOrDefault(Function(c) c.Email = email)  ' Throws if >1 match

' Take/Skip (pagination)
Dim page = orders.OrderBy(Function(o) o.Date) _
    .Skip((pageNumber - 1) * pageSize) _
    .Take(pageSize) _
    .ToList()

' Distinct
Dim uniqueCountries = customers.Select(Function(c) c.Country).Distinct().ToList()
```

## LINQ Performance

```vb
' ✓ Deferred execution - query not executed until enumerated
Dim query = customers.Where(Function(c) c.IsActive)  ' Not executed yet
Dim results = query.ToList()  ' Executed here

' ✓ Use AsQueryable for database queries (enables server-side filtering)
Dim query As IQueryable(Of Customer) = dbContext.Customers _
    .Where(Function(c) c.City = "Boston") _
    .OrderBy(Function(c) c.Name)  ' Translated to SQL

' ✗ AVOID - forces entire table into memory before filtering
Dim customers = dbContext.Customers.ToList() _
    .Where(Function(c) c.City = "Boston")  ' Filters in memory - BAD

' ✓ First/FirstOrDefault vs Single/SingleOrDefault
Dim first = customers.FirstOrDefault()  ' Returns first or Nothing, efficient
Dim single = customers.SingleOrDefault()  ' Checks entire sequence for duplicates, slower
```
