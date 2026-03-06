# Anti-Patterns Gallery

Common coding mistakes with explanations and fixes. Each pattern includes bad/good examples to make code review and refactoring actionable.

---

## Naming Anti-Patterns

### 1. Cryptic Abbreviations

**Problem**: Abbreviations save keystrokes but cost readability. Future readers (including yourself) won't remember what `usrMgr` means.

```typescript
// ❌ Bad
const usrMgr = new UsrMgr();
const cfg = loadCfg();
const btn = document.getElementById('sbmt');
const val = calc(x, y, z);
```

```typescript
// ✅ Good
const userManager = new UserManager();
const config = loadConfig();
const submitButton = document.getElementById('submit');
const totalPrice = calculateTotalPrice(quantity, unitPrice, taxRate);
```

**Rule**: Spell it out. IDE autocomplete makes long names free.

---

### 2. Generic Names

**Problem**: Names like `data`, `info`, `item`, `thing`, `manager`, `handler` tell you nothing about what the code does.

```typescript
// ❌ Bad
function processData(data: any) {
  const info = getData();
  const result = handle(info);
  return result;
}

class Manager {
  items: any[] = [];
  process() { /* ... */ }
}
```

```typescript
// ✅ Good
function validateUserRegistration(registration: UserRegistration) {
  const existingUser = findUserByEmail(registration.email);
  const validationResult = checkEmailAvailability(existingUser);
  return validationResult;
}

class ShoppingCart {
  lineItems: CartLineItem[] = [];
  calculateTotal() { /* ... */ }
}
```

**Rule**: Names should reveal intent. Ask "what does this actually do?"

---

### 3. Misleading Names

**Problem**: Names that lie are worse than bad names. They actively deceive readers.

```typescript
// ❌ Bad - name lies about what it does
function getUserList() {
  // Actually returns a single user, not a list
  return this.currentUser;
}

const isValid = checkDate(date); // Returns the date, not a boolean

class AccountList extends Map { } // It's a Map, not a List
```

```typescript
// ✅ Good - names match behavior
function getCurrentUser() {
  return this.currentUser;
}

const normalizedDate = normalizeDate(date);

class AccountRegistry extends Map { }
```

**Rule**: If the name doesn't match the behavior, change the name (or the behavior).

---

### 4. Hungarian Notation

**Problem**: Encoding types in names was useful in weakly-typed languages. TypeScript makes it redundant and noisy.

```typescript
// ❌ Bad
const strName: string = 'Alice';
const nCount: number = 42;
const arrUsers: User[] = [];
const bIsActive: boolean = true;
interface IUser { } // "I" prefix for interfaces
type TUserRole = 'admin' | 'user'; // "T" prefix for types
```

```typescript
// ✅ Good
const name: string = 'Alice';
const count: number = 42;
const users: User[] = [];
const isActive: boolean = true;
interface User { }
type UserRole = 'admin' | 'user';
```

**Rule**: Let the type system handle types. Names should describe purpose.

---

## Function Anti-Patterns

### 5. God Functions

**Problem**: Functions over 20 lines are hard to understand, test, and modify. They usually do too many things.

```typescript
// ❌ Bad - 50+ line function doing everything
async function processOrder(order: Order) {
  // Validate order
  if (!order.items.length) throw new Error('Empty order');
  if (!order.customer) throw new Error('No customer');
  // ... 10 more validation lines
  
  // Calculate totals
  let subtotal = 0;
  for (const item of order.items) {
    subtotal += item.price * item.quantity;
    // ... discount logic
  }
  // ... 15 more calculation lines
  
  // Process payment
  const paymentResult = await stripe.charge(/* ... */);
  // ... 10 more payment lines
  
  // Send notifications
  await sendEmail(/* ... */);
  await sendSMS(/* ... */);
  // ... more notification logic
  
  // Update inventory
  // ... 10 more lines
  
  return { success: true };
}
```

```typescript
// ✅ Good - composed of small, focused functions
async function processOrder(order: Order) {
  validateOrder(order);
  const totals = calculateOrderTotals(order);
  const payment = await processPayment(order.customer, totals);
  await sendOrderConfirmation(order, payment);
  await updateInventory(order.items);
  return { success: true, orderId: payment.orderId };
}

function validateOrder(order: Order): void {
  if (!order.items.length) throw new Error('Empty order');
  if (!order.customer) throw new Error('No customer');
}

function calculateOrderTotals(order: Order): OrderTotals {
  const subtotal = order.items.reduce(
    (sum, item) => sum + item.price * item.quantity, 0
  );
  return { subtotal, tax: subtotal * 0.1, total: subtotal * 1.1 };
}
```

**Rule**: Extract until each function does exactly one thing.

---

### 6. Too Many Parameters

**Problem**: Functions with 4+ parameters are hard to call correctly and often indicate the function does too much.

```typescript
// ❌ Bad - too many parameters, order matters
function createUser(
  firstName: string,
  lastName: string,
  email: string,
  password: string,
  role: string,
  department: string,
  startDate: Date,
  managerId: string | null,
  isActive: boolean
) {
  // ...
}

// Callers must remember order
createUser('John', 'Doe', 'john@example.com', 'secret', 'admin', 'Engineering', new Date(), null, true);
```

```typescript
// ✅ Good - use an options object
interface CreateUserOptions {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: UserRole;
  department: string;
  startDate?: Date;
  managerId?: string;
  isActive?: boolean;
}

function createUser(options: CreateUserOptions) {
  const { firstName, lastName, email, role, isActive = true } = options;
  // ...
}

// Callers have self-documenting code
createUser({
  firstName: 'John',
  lastName: 'Doe',
  email: 'john@example.com',
  password: 'secret',
  role: 'admin',
  department: 'Engineering',
});
```

**Rule**: More than 3 parameters? Use an options object.

---

### 7. Boolean Flag Parameters

**Problem**: Boolean parameters hide branching logic and make function calls unreadable.

```typescript
// ❌ Bad - what does `true` mean here?
renderButton('Submit', true, false, true);

function renderButton(
  label: string,
  isPrimary: boolean,
  isDisabled: boolean,
  isLoading: boolean
) {
  // Complex branching based on booleans
}
```

```typescript
// ✅ Good - use options object or separate functions
renderButton({
  label: 'Submit',
  variant: 'primary',
  state: 'loading',
});

// Or separate functions for distinct behaviors
renderPrimaryButton('Submit');
renderLoadingButton('Submit');

// Or use enums
type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonState = 'default' | 'loading' | 'disabled';
```

**Rule**: Boolean parameters should be in an options object with named properties.

---

### 8. Side Effects in Getters

**Problem**: Getters that modify state violate the principle of least surprise. Readers expect getters to be pure.

```typescript
// ❌ Bad - getter with hidden side effect
class ShoppingCart {
  private _items: CartItem[] = [];
  private _lastAccessed: Date;

  get items() {
    this._lastAccessed = new Date(); // Side effect!
    this.logAccess(); // Another side effect!
    return this._items;
  }

  get totalPrice() {
    this.recalculateDiscounts(); // Mutation!
    return this._items.reduce((sum, i) => sum + i.price, 0);
  }
}
```

```typescript
// ✅ Good - getters are pure, side effects are explicit
class ShoppingCart {
  private _items: CartItem[] = [];
  private _lastAccessed: Date;

  get items() {
    return this._items;
  }

  get totalPrice() {
    return this._items.reduce((sum, i) => sum + i.price, 0);
  }

  recordAccess() {
    this._lastAccessed = new Date();
    this.logAccess();
  }

  applyDiscounts() {
    this.recalculateDiscounts();
  }
}
```

**Rule**: Getters should be pure. Make side effects explicit with verbs.

---

### 9. Returning Different Types

**Problem**: Functions that return different types based on conditions make code unpredictable and hard to type.

```typescript
// ❌ Bad - return type depends on runtime condition
function getUser(id: string) {
  const user = database.find(id);
  if (!user) {
    return false; // boolean
  }
  if (user.isDeleted) {
    return null; // null
  }
  return user; // User object
}

// Caller must handle all cases
const result = getUser('123');
if (result === false) { /* not found */ }
else if (result === null) { /* deleted */ }
else { /* use result.name */ }
```

```typescript
// ✅ Good - consistent return type with discriminated union
type GetUserResult =
  | { status: 'found'; user: User }
  | { status: 'not_found' }
  | { status: 'deleted' };

function getUser(id: string): GetUserResult {
  const user = database.find(id);
  if (!user) {
    return { status: 'not_found' };
  }
  if (user.isDeleted) {
    return { status: 'deleted' };
  }
  return { status: 'found', user };
}

// Caller has type-safe handling
const result = getUser('123');
if (result.status === 'found') {
  console.log(result.user.name); // TypeScript knows user exists
}
```

**Rule**: Return consistent types. Use discriminated unions for multiple outcomes.

---

## Structure Anti-Patterns

### 10. Deep Nesting (Pyramid of Doom)

**Problem**: Deeply nested code is hard to follow and usually indicates missing abstractions.

```typescript
// ❌ Bad - 5 levels deep
function processOrder(order: Order) {
  if (order) {
    if (order.items.length > 0) {
      if (order.customer) {
        if (order.customer.isVerified) {
          if (order.paymentMethod) {
            // Finally, the actual logic buried 5 levels deep
            return submitOrder(order);
          } else {
            throw new Error('No payment method');
          }
        } else {
          throw new Error('Customer not verified');
        }
      } else {
        throw new Error('No customer');
      }
    } else {
      throw new Error('No items');
    }
  } else {
    throw new Error('No order');
  }
}
```

```typescript
// ✅ Good - guard clauses flatten the structure
function processOrder(order: Order) {
  if (!order) throw new Error('No order');
  if (!order.items.length) throw new Error('No items');
  if (!order.customer) throw new Error('No customer');
  if (!order.customer.isVerified) throw new Error('Customer not verified');
  if (!order.paymentMethod) throw new Error('No payment method');

  return submitOrder(order);
}
```

**Rule**: Use guard clauses for early returns. Max 2 levels of nesting.

---

### 11. Premature Abstraction

**Problem**: Creating abstractions before you understand the problem leads to wrong abstractions that are hard to change.

```typescript
// ❌ Bad - abstraction created for one use case
interface DataFetcher<T> {
  fetch(): Promise<T>;
  cache(): void;
  invalidate(): void;
}

class GenericRepository<T> implements DataFetcher<T> {
  constructor(private adapter: StorageAdapter<T>) {}
  // ... complex implementation
}

// Used exactly once:
const userRepo = new GenericRepository(new UserAdapter());
```

```typescript
// ✅ Good - start simple, abstract when patterns emerge
// First implementation: just fetch users
async function fetchUsers(): Promise<User[]> {
  return await db.query('SELECT * FROM users');
}

// Later, if you need caching, add it:
async function fetchUsersWithCache(): Promise<User[]> {
  const cached = cache.get('users');
  if (cached) return cached;
  
  const users = await db.query('SELECT * FROM users');
  cache.set('users', users);
  return users;
}

// Abstract only when you see the SAME pattern 3+ times
```

**Rule**: "Duplication is far cheaper than the wrong abstraction." - Sandi Metz

---

### 12. Over-Engineering

**Problem**: Building for hypothetical future requirements adds complexity without value.

```typescript
// ❌ Bad - enterprise FizzBuzz
interface FizzBuzzStrategy {
  applies(n: number): boolean;
  execute(n: number): string;
}

class FizzStrategy implements FizzBuzzStrategy {
  applies(n: number) { return n % 3 === 0; }
  execute() { return 'Fizz'; }
}

class BuzzStrategy implements FizzBuzzStrategy {
  applies(n: number) { return n % 5 === 0; }
  execute() { return 'Buzz'; }
}

class FizzBuzzProcessor {
  constructor(private strategies: FizzBuzzStrategy[]) {}
  process(n: number): string {
    return this.strategies
      .filter(s => s.applies(n))
      .map(s => s.execute(n))
      .join('') || String(n);
  }
}

const processor = new FizzBuzzProcessor([
  new FizzStrategy(),
  new BuzzStrategy(),
]);
```

```typescript
// ✅ Good - solve the actual problem
function fizzBuzz(n: number): string {
  if (n % 15 === 0) return 'FizzBuzz';
  if (n % 3 === 0) return 'Fizz';
  if (n % 5 === 0) return 'Buzz';
  return String(n);
}
```

**Rule**: Solve today's problem. Refactor when requirements actually change.

---

### 13. Copy-Paste Programming

**Problem**: Duplicated code means duplicated bugs and maintenance burden.

```typescript
// ❌ Bad - same validation logic copied
function createUser(data: UserInput) {
  if (!data.email) throw new Error('Email required');
  if (!data.email.includes('@')) throw new Error('Invalid email');
  if (data.email.length > 255) throw new Error('Email too long');
  // ... create user
}

function updateUser(id: string, data: UserInput) {
  if (!data.email) throw new Error('Email required');
  if (!data.email.includes('@')) throw new Error('Invalid email');
  if (data.email.length > 255) throw new Error('Email too long');
  // ... update user
}

function inviteUser(data: UserInput) {
  if (!data.email) throw new Error('Email required');
  if (!data.email.includes('@')) throw new Error('Invalid email');
  if (data.email.length > 255) throw new Error('Email too long');
  // ... invite user
}
```

```typescript
// ✅ Good - extract shared logic
function validateEmail(email: string): void {
  if (!email) throw new Error('Email required');
  if (!email.includes('@')) throw new Error('Invalid email');
  if (email.length > 255) throw new Error('Email too long');
}

function createUser(data: UserInput) {
  validateEmail(data.email);
  // ... create user
}

function updateUser(id: string, data: UserInput) {
  validateEmail(data.email);
  // ... update user
}

function inviteUser(data: UserInput) {
  validateEmail(data.email);
  // ... invite user
}
```

**Rule**: If you copy-paste, you're probably missing an abstraction.

---

### 14. God Objects

**Problem**: Classes that know too much and do too much become unmaintainable.

```typescript
// ❌ Bad - class does everything
class ApplicationManager {
  users: User[] = [];
  orders: Order[] = [];
  products: Product[] = [];
  
  // User operations
  createUser() { /* ... */ }
  deleteUser() { /* ... */ }
  authenticateUser() { /* ... */ }
  
  // Order operations
  createOrder() { /* ... */ }
  cancelOrder() { /* ... */ }
  refundOrder() { /* ... */ }
  
  // Product operations
  addProduct() { /* ... */ }
  updateInventory() { /* ... */ }
  
  // Reporting
  generateSalesReport() { /* ... */ }
  generateUserReport() { /* ... */ }
  
  // Notifications
  sendEmail() { /* ... */ }
  sendSMS() { /* ... */ }
}
```

```typescript
// ✅ Good - separate concerns
class UserService {
  createUser() { /* ... */ }
  deleteUser() { /* ... */ }
}

class AuthService {
  authenticate() { /* ... */ }
}

class OrderService {
  createOrder() { /* ... */ }
  cancelOrder() { /* ... */ }
}

class NotificationService {
  sendEmail() { /* ... */ }
  sendSMS() { /* ... */ }
}
```

**Rule**: Each class should have one reason to change.

---

## Comment Anti-Patterns

### 15. Commented-Out Code

**Problem**: Commented code is dead code. It confuses readers and never gets cleaned up.

```typescript
// ❌ Bad
function calculateTotal(items: Item[]) {
  let total = 0;
  for (const item of items) {
    total += item.price;
    // total += item.price * item.quantity; // Old calculation
    // if (item.discount) {
    //   total -= item.discount;
    // }
  }
  // return total * 1.1; // With tax
  // return total * 1.08; // Old tax rate
  return total;
}
```

```typescript
// ✅ Good - delete it, git remembers
function calculateTotal(items: Item[]) {
  return items.reduce((total, item) => total + item.price, 0);
}
```

**Rule**: Delete commented code. Use version control for history.

---

### 16. Obvious Comments

**Problem**: Comments that restate the code add noise without value.

```typescript
// ❌ Bad - comments that add nothing
// Increment counter
counter++;

// Check if user is null
if (user === null) {
  // Return early
  return;
}

// Loop through all items
for (const item of items) {
  // Add item price to total
  total += item.price;
}
```

```typescript
// ✅ Good - code is self-documenting, comments explain WHY
counter++; // No comment needed

if (!user) return;

const total = items.reduce((sum, item) => sum + item.price, 0);

// Business rule: Premium members get early access 48 hours before launch
if (user.isPremium && hoursUntilLaunch < 48) {
  showEarlyAccess();
}
```

**Rule**: Don't comment WHAT, comment WHY (if not obvious).

---

### 17. TODO Sprawl

**Problem**: TODOs accumulate and never get done. They become invisible noise.

```typescript
// ❌ Bad - TODO graveyard
function processPayment(amount: number) {
  // TODO: Add retry logic
  // TODO: Handle currency conversion
  // TODO: Add logging
  // TODO: Optimize this (added 2019)
  // FIXME: This is broken sometimes
  // HACK: Temporary fix, remove later
  // XXX: Why does this work?
  return charge(amount);
}
```

```typescript
// ✅ Good - TODOs are tracked in issues, not code
function processPayment(amount: number) {
  // See JIRA-1234 for planned retry logic
  return charge(amount);
}

// Or just fix it now:
async function processPayment(amount: number) {
  return await retry(() => charge(amount), { attempts: 3 });
}
```

**Rule**: TODOs belong in your issue tracker, not your code.

---

### 18. Outdated Comments

**Problem**: Comments that contradict the code are actively harmful.

```typescript
// ❌ Bad - comment lies about the code
// Returns the user's full name (first + last)
function getUserName(user: User): string {
  return user.email; // Actually returns email!
}

// Validates and saves the user
function processUser(user: User) {
  // No validation, just saves
  database.save(user);
}

// This function is deprecated, use newFunction() instead
function oldFunction() {
  // Still actively used throughout codebase
}
```

```typescript
// ✅ Good - update or remove outdated comments
function getUserEmail(user: User): string {
  return user.email;
}

function saveUser(user: User) {
  database.save(user);
}

/** @deprecated Use {@link newFunction} instead */
function oldFunction() {
  console.warn('oldFunction is deprecated');
  return newFunction();
}
```

**Rule**: When you change code, update or delete related comments.

---

## Control Flow Anti-Patterns

### 19. Exception-Driven Control Flow

**Problem**: Using exceptions for normal control flow is slow and hard to follow.

```typescript
// ❌ Bad - exceptions for expected cases
function findUser(id: string): User {
  try {
    return database.getUser(id);
  } catch {
    try {
      return cache.getUser(id);
    } catch {
      try {
        return createDefaultUser(id);
      } catch {
        throw new Error('Cannot get user');
      }
    }
  }
}
```

```typescript
// ✅ Good - explicit control flow
function findUser(id: string): User | null {
  const dbUser = database.getUser(id);
  if (dbUser) return dbUser;

  const cachedUser = cache.getUser(id);
  if (cachedUser) return cachedUser;

  return createDefaultUser(id);
}
```

**Rule**: Exceptions are for exceptional situations, not control flow.

---

### 20. Stringly-Typed Code

**Problem**: Using strings where enums or types would be safer leads to typos and missing cases.

```typescript
// ❌ Bad - magic strings everywhere
function handleStatus(status: string) {
  if (status === 'pending') { /* ... */ }
  else if (status === 'Pending') { /* ... */ } // Typo variant
  else if (status === 'active') { /* ... */ }
  else if (status === 'actve') { /* ... */ } // Typo!
}

user.role = 'admni'; // Typo, no error!
```

```typescript
// ✅ Good - type-safe enums or unions
type Status = 'pending' | 'active' | 'completed' | 'cancelled';
type UserRole = 'admin' | 'user' | 'guest';

function handleStatus(status: Status) {
  switch (status) {
    case 'pending': /* ... */ break;
    case 'active': /* ... */ break;
    case 'completed': /* ... */ break;
    case 'cancelled': /* ... */ break;
    // TypeScript ensures exhaustive handling
  }
}

user.role = 'admni'; // TypeScript error!
```

**Rule**: Use types instead of strings for fixed sets of values.

---

### 21. Callback Hell

**Problem**: Nested callbacks create unreadable, hard-to-debug code.

```typescript
// ❌ Bad - callback pyramid
getUser(userId, (err, user) => {
  if (err) return handleError(err);
  getOrders(user.id, (err, orders) => {
    if (err) return handleError(err);
    getOrderDetails(orders[0].id, (err, details) => {
      if (err) return handleError(err);
      processDetails(details, (err, result) => {
        if (err) return handleError(err);
        sendNotification(result, (err) => {
          if (err) return handleError(err);
          console.log('Done!');
        });
      });
    });
  });
});
```

```typescript
// ✅ Good - async/await
async function processUserOrder(userId: string) {
  try {
    const user = await getUser(userId);
    const orders = await getOrders(user.id);
    const details = await getOrderDetails(orders[0].id);
    const result = await processDetails(details);
    await sendNotification(result);
    console.log('Done!');
  } catch (error) {
    handleError(error);
  }
}
```

**Rule**: Use async/await for asynchronous code.

---

## Quick Reference

| Anti-Pattern | Fix |
|--------------|-----|
| Cryptic abbreviations | Spell it out |
| Generic names | Reveal intent |
| Misleading names | Match name to behavior |
| Hungarian notation | Let types handle types |
| God functions | Extract smaller functions |
| Too many parameters | Use options object |
| Boolean flags | Named options or separate functions |
| Side effects in getters | Make mutations explicit |
| Different return types | Use discriminated unions |
| Deep nesting | Guard clauses |
| Premature abstraction | Wait for patterns to emerge |
| Over-engineering | Solve today's problem |
| Copy-paste | Extract shared logic |
| God objects | Single responsibility |
| Commented-out code | Delete it |
| Obvious comments | Let code self-document |
| TODO sprawl | Use issue tracker |
| Outdated comments | Update or delete |
| Exception control flow | Explicit conditionals |
| Stringly-typed | Use enums/unions |
| Callback hell | async/await |
