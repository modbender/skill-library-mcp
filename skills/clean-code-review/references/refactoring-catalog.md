# Refactoring Catalog

Essential refactoring patterns with before/after examples. Each refactoring is a small, reversible transformation that improves code structure without changing behavior.

Based on Martin Fowler's refactoring catalog with TypeScript examples.

---

## Composing Methods

Break down large methods into smaller, focused pieces.

### Extract Function

**Motivation**: A code fragment that can be grouped together and named. The most common refactoring.

**When to use**:
- Code block has a comment explaining what it does
- Same code appears in multiple places
- Function is too long (20+ lines)
- Logic is at a different level of abstraction

```typescript
// Before
function printInvoice(invoice: Invoice) {
  console.log('=================');
  console.log('=== INVOICE =====');
  console.log('=================');
  
  // Print details
  console.log(`Customer: ${invoice.customer}`);
  console.log(`Date: ${invoice.date}`);
  
  // Calculate total
  let total = 0;
  for (const item of invoice.items) {
    total += item.price * item.quantity;
  }
  console.log(`Total: $${total}`);
  
  console.log('=================');
}
```

```typescript
// After
function printInvoice(invoice: Invoice) {
  printHeader();
  printDetails(invoice);
  printTotal(invoice);
  printFooter();
}

function printHeader() {
  console.log('=================');
  console.log('=== INVOICE =====');
  console.log('=================');
}

function printDetails(invoice: Invoice) {
  console.log(`Customer: ${invoice.customer}`);
  console.log(`Date: ${invoice.date}`);
}

function printTotal(invoice: Invoice) {
  const total = calculateTotal(invoice.items);
  console.log(`Total: $${total}`);
}

function calculateTotal(items: InvoiceItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function printFooter() {
  console.log('=================');
}
```

**Mechanics**:
1. Create new function named after what it does (not how)
2. Copy the code fragment to the new function
3. Pass any needed variables as parameters
4. Replace the original code with a call to the new function

---

### Inline Function

**Motivation**: The opposite of Extract Function. The function body is as clear as the name, or the function is only delegating.

**When to use**:
- Function body is as obvious as its name
- You have a group of badly factored functions and want to re-extract differently
- Too much indirection

```typescript
// Before
function moreThanFiveOrders(customer: Customer): boolean {
  return customer.orders.length > 5;
}

function getDiscount(customer: Customer): number {
  if (moreThanFiveOrders(customer)) {
    return 0.1;
  }
  return 0;
}
```

```typescript
// After
function getDiscount(customer: Customer): number {
  if (customer.orders.length > 5) {
    return 0.1;
  }
  return 0;
}
```

**Mechanics**:
1. Check function isn't polymorphic (overridden in subclasses)
2. Find all callers
3. Replace each call with the function body
4. Delete the function

---

### Replace Temp with Query

**Motivation**: Temporary variables can be a problem—they make functions longer and block Extract Function.

**When to use**:
- A temp is assigned once and used multiple times
- The calculation could be a method
- You want to extract part of a function

```typescript
// Before
function getPrice(order: Order): number {
  const basePrice = order.quantity * order.itemPrice;
  const discount = Math.max(0, order.quantity - 100) * order.itemPrice * 0.05;
  const shipping = Math.min(basePrice * 0.1, 50);
  return basePrice - discount + shipping;
}
```

```typescript
// After
function getPrice(order: Order): number {
  return basePrice(order) - discount(order) + shipping(order);
}

function basePrice(order: Order): number {
  return order.quantity * order.itemPrice;
}

function discount(order: Order): number {
  return Math.max(0, order.quantity - 100) * order.itemPrice * 0.05;
}

function shipping(order: Order): number {
  return Math.min(basePrice(order) * 0.1, 50);
}
```

**Mechanics**:
1. Check the temp is only assigned once
2. Extract the assignment into a function
3. Replace references to the temp with function calls
4. Remove the temp declaration

---

### Introduce Explaining Variable

**Motivation**: Complex expressions are hard to read. Break them into named pieces.

**When to use**:
- A complex expression that's hard to understand
- Multiple conditions in an if statement
- Mathematical formulas

```typescript
// Before
function calculatePrice(order: Order): number {
  return order.quantity * order.itemPrice -
    Math.max(0, order.quantity - 100) * order.itemPrice * 0.05 +
    Math.min(order.quantity * order.itemPrice * 0.1, 50);
}

function isEligibleForDiscount(user: User): boolean {
  return user.age >= 65 || 
    (user.memberSince < new Date('2020-01-01') && user.purchaseCount > 10) ||
    user.isEmployee;
}
```

```typescript
// After
function calculatePrice(order: Order): number {
  const basePrice = order.quantity * order.itemPrice;
  const quantityDiscount = Math.max(0, order.quantity - 100) * order.itemPrice * 0.05;
  const shipping = Math.min(basePrice * 0.1, 50);
  return basePrice - quantityDiscount + shipping;
}

function isEligibleForDiscount(user: User): boolean {
  const isSenior = user.age >= 65;
  const isLoyalCustomer = user.memberSince < new Date('2020-01-01') && 
                          user.purchaseCount > 10;
  const isEmployee = user.isEmployee;
  
  return isSenior || isLoyalCustomer || isEmployee;
}
```

**Mechanics**:
1. Identify a complex expression or sub-expression
2. Create a variable with a meaningful name
3. Assign the expression to the variable
4. Replace the expression with the variable

---

## Moving Features

Move code to where it belongs.

### Move Function

**Motivation**: Functions should live with the data they use most.

**When to use**:
- Function uses more features of another class
- Function is in the wrong module
- Coupling would be reduced by moving

```typescript
// Before - calculateInterest uses account data, not the calculator's
class InterestCalculator {
  calculateInterest(account: Account, days: number): number {
    const balance = account.getBalance();
    const rate = account.getInterestRate();
    const type = account.getType();
    
    if (type === 'savings') {
      return balance * rate * days / 365;
    } else if (type === 'checking') {
      return balance * (rate - 0.01) * days / 365;
    }
    return 0;
  }
}
```

```typescript
// After - method moved to Account where the data lives
class Account {
  private balance: number;
  private interestRate: number;
  private type: 'savings' | 'checking';
  
  calculateInterest(days: number): number {
    if (this.type === 'savings') {
      return this.balance * this.interestRate * days / 365;
    } else if (this.type === 'checking') {
      return this.balance * (this.interestRate - 0.01) * days / 365;
    }
    return 0;
  }
}
```

**Mechanics**:
1. Look at what the function references—does it use more from elsewhere?
2. Check if it should be a method on one of its arguments
3. Move the function
4. Update all callers

---

### Extract Class

**Motivation**: A class is doing too much. Split it based on responsibilities.

**When to use**:
- Class has too many fields
- Class has too many methods
- Subsets of data/methods are used together
- Class name includes "And" or "Manager"

```typescript
// Before - Person has phone-related responsibilities mixed in
class Person {
  name: string;
  
  // These belong together
  officeAreaCode: string;
  officeNumber: string;
  
  // And these
  homeAreaCode: string;
  homeNumber: string;
  
  getOfficePhone(): string {
    return `(${this.officeAreaCode}) ${this.officeNumber}`;
  }
  
  getHomePhone(): string {
    return `(${this.homeAreaCode}) ${this.homeNumber}`;
  }
}
```

```typescript
// After - Phone is its own class
class PhoneNumber {
  constructor(
    private areaCode: string,
    private number: string
  ) {}
  
  format(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}

class Person {
  name: string;
  officePhone: PhoneNumber;
  homePhone: PhoneNumber;
  
  getOfficePhone(): string {
    return this.officePhone.format();
  }
  
  getHomePhone(): string {
    return this.homePhone.format();
  }
}
```

**Mechanics**:
1. Identify a subset of data and methods that belong together
2. Create a new class
3. Move fields and methods to the new class
4. Create a link from old class to new class

---

### Hide Delegate

**Motivation**: Reduce coupling by hiding the object structure from clients.

**When to use**:
- Clients navigate through one object to get to another
- Changes to the delegate affect all clients
- You're exposing internal structure

```typescript
// Before - Client knows about internal structure
class Person {
  department: Department;
}

class Department {
  manager: Person;
}

// Client code - knows too much about structure
const manager = person.department.manager;
```

```typescript
// After - Person hides the delegation
class Person {
  private department: Department;
  
  getManager(): Person {
    return this.department.manager;
  }
}

// Client code - simpler, less coupled
const manager = person.getManager();
```

**Mechanics**:
1. Create a delegating method on the server
2. Replace client calls to the delegate with calls to the server
3. Consider making the delegate field private

---

## Organizing Data

Improve how data is structured and accessed.

### Replace Magic Number with Constant

**Motivation**: Magic numbers obscure meaning and are easy to mistype.

**When to use**:
- Numbers appear in code without explanation
- Same number appears in multiple places
- The number has domain meaning

```typescript
// Before
function potentialEnergy(mass: number, height: number): number {
  return mass * height * 9.81;
}

function calculateDiscount(total: number): number {
  if (total > 100) {
    return total * 0.1;
  }
  return 0;
}
```

```typescript
// After
const GRAVITATIONAL_CONSTANT = 9.81;
const DISCOUNT_THRESHOLD = 100;
const DISCOUNT_RATE = 0.1;

function potentialEnergy(mass: number, height: number): number {
  return mass * height * GRAVITATIONAL_CONSTANT;
}

function calculateDiscount(total: number): number {
  if (total > DISCOUNT_THRESHOLD) {
    return total * DISCOUNT_RATE;
  }
  return 0;
}
```

**Mechanics**:
1. Create a constant with a meaningful name
2. Replace the magic number with the constant
3. Search for other occurrences of the same number

---

### Replace Primitive with Object

**Motivation**: Primitives with behavior should be objects.

**When to use**:
- Same validation logic for a primitive appears multiple times
- Formatting/parsing logic is scattered
- The value has business rules

```typescript
// Before - phone validation scattered everywhere
function validateOrder(order: Order) {
  const phone = order.phone;
  if (!phone.match(/^\d{10}$/)) {
    throw new Error('Invalid phone');
  }
}

function formatPhone(phone: string): string {
  return `(${phone.slice(0,3)}) ${phone.slice(3,6)}-${phone.slice(6)}`;
}
```

```typescript
// After - PhoneNumber encapsulates all behavior
class PhoneNumber {
  private readonly value: string;
  
  constructor(phone: string) {
    if (!phone.match(/^\d{10}$/)) {
      throw new Error('Invalid phone number');
    }
    this.value = phone;
  }
  
  format(): string {
    return `(${this.value.slice(0,3)}) ${this.value.slice(3,6)}-${this.value.slice(6)}`;
  }
  
  getAreaCode(): string {
    return this.value.slice(0, 3);
  }
  
  toString(): string {
    return this.value;
  }
}

// Usage
const phone = new PhoneNumber('5551234567');
console.log(phone.format()); // (555) 123-4567
```

**Mechanics**:
1. Create a class for the value
2. Add validation in constructor
3. Add any formatting/parsing methods
4. Replace usages of the primitive

---

### Encapsulate Collection

**Motivation**: Exposing a collection allows clients to modify it without the owner knowing.

**When to use**:
- A getter returns a raw collection
- Clients are adding/removing items directly
- Collection modifications should trigger other behavior

```typescript
// Before - collection exposed directly
class Course {
  name: string;
}

class Person {
  courses: Course[] = [];
  
  getCourses(): Course[] {
    return this.courses; // Returns mutable reference!
  }
}

// Client can bypass the Person
person.getCourses().push(newCourse);
person.getCourses().length = 0; // Dangerous!
```

```typescript
// After - collection encapsulated
class Person {
  private courses: Course[] = [];
  
  getCourses(): readonly Course[] {
    return [...this.courses]; // Return copy
  }
  
  addCourse(course: Course): void {
    this.courses.push(course);
    // Can add validation, events, logging here
  }
  
  removeCourse(course: Course): void {
    const index = this.courses.indexOf(course);
    if (index > -1) {
      this.courses.splice(index, 1);
    }
  }
  
  get numberOfCourses(): number {
    return this.courses.length;
  }
}
```

**Mechanics**:
1. Add methods for modifying the collection
2. Return a copy or readonly view from the getter
3. Replace direct modifications with method calls

---

## Simplifying Conditionals

Make conditional logic easier to understand.

### Decompose Conditional

**Motivation**: Complex conditionals are hard to read. Extract into well-named functions.

**When to use**:
- Conditional has complex conditions
- Then/else branches have substantial code
- The logic isn't immediately clear

```typescript
// Before
function calculateCharge(date: Date, quantity: number): number {
  if (date.getMonth() >= 5 && date.getMonth() <= 8) {
    return quantity * 1.2 + (quantity > 100 ? quantity * 0.05 : 0);
  } else {
    return quantity * 1.0 + (quantity > 50 ? quantity * 0.03 : 0);
  }
}
```

```typescript
// After
function calculateCharge(date: Date, quantity: number): number {
  if (isSummer(date)) {
    return summerCharge(quantity);
  } else {
    return regularCharge(quantity);
  }
}

function isSummer(date: Date): boolean {
  return date.getMonth() >= 5 && date.getMonth() <= 8;
}

function summerCharge(quantity: number): number {
  const baseCharge = quantity * 1.2;
  const bulkDiscount = quantity > 100 ? quantity * 0.05 : 0;
  return baseCharge + bulkDiscount;
}

function regularCharge(quantity: number): number {
  const baseCharge = quantity * 1.0;
  const bulkDiscount = quantity > 50 ? quantity * 0.03 : 0;
  return baseCharge + bulkDiscount;
}
```

**Mechanics**:
1. Extract the condition into a function
2. Extract the then-branch into a function
3. Extract the else-branch into a function

---

### Consolidate Conditional Expression

**Motivation**: Multiple conditions with the same result should be combined.

**When to use**:
- Several conditions return the same value
- The conditions are really checking one thing
- Combining makes intent clearer

```typescript
// Before
function disabilityAmount(employee: Employee): number {
  if (employee.seniority < 2) return 0;
  if (employee.monthsDisabled > 12) return 0;
  if (employee.isPartTime) return 0;
  // Calculate disability
  return employee.salary * 0.6;
}
```

```typescript
// After
function disabilityAmount(employee: Employee): number {
  if (isNotEligibleForDisability(employee)) return 0;
  return employee.salary * 0.6;
}

function isNotEligibleForDisability(employee: Employee): boolean {
  return employee.seniority < 2 ||
         employee.monthsDisabled > 12 ||
         employee.isPartTime;
}
```

**Mechanics**:
1. Combine conditions using logical operators
2. Extract the combined condition into a function
3. Give it a meaningful name

---

### Replace Nested Conditional with Guard Clauses

**Motivation**: Deeply nested conditionals are hard to follow. Use early returns.

**When to use**:
- Deep nesting (more than 2 levels)
- Some branches are exceptional/edge cases
- Happy path is buried in else clauses

```typescript
// Before - nested pyramid
function getPayAmount(employee: Employee): number {
  let result: number;
  if (employee.isSeparated) {
    result = 0;
  } else {
    if (employee.isRetired) {
      result = employee.pension;
    } else {
      if (employee.isOnLeave) {
        result = employee.salary * 0.5;
      } else {
        result = employee.salary;
      }
    }
  }
  return result;
}
```

```typescript
// After - flat with guard clauses
function getPayAmount(employee: Employee): number {
  if (employee.isSeparated) return 0;
  if (employee.isRetired) return employee.pension;
  if (employee.isOnLeave) return employee.salary * 0.5;
  return employee.salary;
}
```

**Mechanics**:
1. Identify edge cases
2. Replace each with a guard clause (early return)
3. Remove unnecessary else clauses

---

### Replace Conditional with Polymorphism

**Motivation**: Type-based conditionals often indicate missing polymorphism.

**When to use**:
- Switching on type code
- Same switch appears in multiple places
- Each case has substantially different behavior

```typescript
// Before
type BirdType = 'european' | 'african' | 'norwegian_blue';

function getSpeed(bird: { type: BirdType; voltage?: number }): number {
  switch (bird.type) {
    case 'european':
      return 35;
    case 'african':
      return 40 - 2 * bird.numberOfCoconuts;
    case 'norwegian_blue':
      return bird.voltage > 100 ? 20 : 0;
    default:
      return 0;
  }
}

function getPlumage(bird: { type: BirdType }): string {
  switch (bird.type) {
    case 'european':
      return 'average';
    case 'african':
      return bird.numberOfCoconuts > 2 ? 'tired' : 'average';
    case 'norwegian_blue':
      return bird.voltage > 100 ? 'scorched' : 'beautiful';
    default:
      return 'unknown';
  }
}
```

```typescript
// After
interface Bird {
  getSpeed(): number;
  getPlumage(): string;
}

class EuropeanSwallow implements Bird {
  getSpeed() { return 35; }
  getPlumage() { return 'average'; }
}

class AfricanSwallow implements Bird {
  constructor(private numberOfCoconuts: number) {}
  
  getSpeed() { return 40 - 2 * this.numberOfCoconuts; }
  getPlumage() { return this.numberOfCoconuts > 2 ? 'tired' : 'average'; }
}

class NorwegianBlueParrot implements Bird {
  constructor(private voltage: number) {}
  
  getSpeed() { return this.voltage > 100 ? 20 : 0; }
  getPlumage() { return this.voltage > 100 ? 'scorched' : 'beautiful'; }
}

// Factory to create the right type
function createBird(data: BirdData): Bird {
  switch (data.type) {
    case 'european': return new EuropeanSwallow();
    case 'african': return new AfricanSwallow(data.numberOfCoconuts);
    case 'norwegian_blue': return new NorwegianBlueParrot(data.voltage);
  }
}
```

**Mechanics**:
1. Create interface/base class
2. Create a class for each type
3. Move switch logic into each class
4. Replace switch with polymorphic call

---

## Simplifying Function Calls

Make functions easier to call and understand.

### Rename Function

**Motivation**: Good names are the best documentation. If you can't name it, you don't understand it.

**When to use**:
- Name doesn't describe what the function does
- Name is misleading
- Name is too technical for the domain

```typescript
// Before - unclear names
function calc(a: number, b: number): number { /* ... */ }
function process(data: unknown): void { /* ... */ }
function handle(event: Event): void { /* ... */ }
function inv(customer: Customer): Invoice { /* ... */ }
```

```typescript
// After - descriptive names
function calculateCompoundInterest(principal: number, rate: number): number { /* ... */ }
function validateAndSaveUserProfile(profile: UserProfile): void { /* ... */ }
function trackButtonClick(event: MouseEvent): void { /* ... */ }
function generateInvoiceForCustomer(customer: Customer): Invoice { /* ... */ }
```

**Mechanics**:
1. Choose a better name (this is the hard part)
2. Create new function with new name
3. Copy body to new function
4. Update all callers
5. Remove old function

---

### Introduce Parameter Object

**Motivation**: Groups of parameters that travel together should be a single object.

**When to use**:
- Same group of parameters appears in multiple functions
- Parameters have a clear relationship
- You want to add behavior to the group

```typescript
// Before - date range parameters everywhere
function getTotalSales(startDate: Date, endDate: Date): number { /* ... */ }
function getAverageOrders(startDate: Date, endDate: Date): number { /* ... */ }
function generateReport(startDate: Date, endDate: Date, format: string): Report { /* ... */ }
```

```typescript
// After - DateRange object
class DateRange {
  constructor(
    readonly start: Date,
    readonly end: Date
  ) {
    if (start > end) throw new Error('Invalid date range');
  }
  
  contains(date: Date): boolean {
    return date >= this.start && date <= this.end;
  }
  
  get durationInDays(): number {
    const ms = this.end.getTime() - this.start.getTime();
    return Math.ceil(ms / (1000 * 60 * 60 * 24));
  }
}

function getTotalSales(dateRange: DateRange): number { /* ... */ }
function getAverageOrders(dateRange: DateRange): number { /* ... */ }
function generateReport(dateRange: DateRange, format: string): Report { /* ... */ }
```

**Mechanics**:
1. Create a class for the parameter group
2. Add validation in constructor
3. Add any relevant methods
4. Replace parameter lists with the new object

---

### Replace Parameter with Method

**Motivation**: A parameter that can be derived from other available information is redundant.

**When to use**:
- Parameter value is derived from something else
- Parameter requires complex calculation by caller
- You're passing internal state back in

```typescript
// Before - caller computes discountRate
function getFinalPrice(
  basePrice: number,
  discountLevel: number,
  discountRate: number
): number {
  return basePrice - (basePrice * discountRate);
}

// Caller has to know how to calculate rate
const rate = getDiscountRate(customer.discountLevel);
const price = getFinalPrice(basePrice, customer.discountLevel, rate);
```

```typescript
// After - function derives discountRate internally
function getFinalPrice(basePrice: number, discountLevel: number): number {
  const discountRate = getDiscountRate(discountLevel);
  return basePrice - (basePrice * discountRate);
}

// Caller is simpler
const price = getFinalPrice(basePrice, customer.discountLevel);
```

**Mechanics**:
1. Extract the parameter calculation into a method
2. Call that method inside the function
3. Remove the parameter

---

## Quick Reference

| Category | Refactoring | When to Use |
|----------|-------------|-------------|
| **Composing Methods** | Extract Function | Code block can be named |
| | Inline Function | Body is clear as name |
| | Replace Temp with Query | Temp blocks extraction |
| | Introduce Explaining Variable | Complex expression |
| **Moving Features** | Move Function | Uses other class's data |
| | Extract Class | Class does too much |
| | Hide Delegate | Clients navigate too deep |
| **Organizing Data** | Replace Magic Number | Unexplained numbers |
| | Replace Primitive with Object | Primitive has behavior |
| | Encapsulate Collection | Exposed mutable collection |
| **Simplifying Conditionals** | Decompose Conditional | Complex if-then-else |
| | Consolidate Conditional | Same result, multiple checks |
| | Guard Clauses | Deep nesting |
| | Replace with Polymorphism | Switch on type |
| **Function Calls** | Rename Function | Name doesn't fit |
| | Parameter Object | Params travel together |
| | Replace Parameter with Method | Param can be derived |

---

## Refactoring Workflow

1. **Ensure tests pass** before starting
2. **Make one small change** at a time
3. **Run tests** after each change
4. **Commit frequently** so you can revert
5. **Never refactor and add features** in the same commit
