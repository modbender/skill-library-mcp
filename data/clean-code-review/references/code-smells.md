# Code Smells Catalog

Code smells are symptoms that indicate deeper problems. They're not bugs—the code works—but they signal design issues that make code harder to understand, change, and maintain.

Based on Martin Fowler's refactoring catalog with TypeScript examples.

---

## Bloaters

Code that has grown too large to work with effectively.

### Long Method

**Symptoms**:
- Function exceeds 20 lines
- Multiple levels of abstraction in one function
- Comments separating "sections" within a function
- Difficult to name—does too many things

```typescript
// ❌ Smell: Long method with multiple responsibilities
async function processCheckout(cart: Cart, user: User) {
  // Validate cart
  if (!cart.items.length) throw new Error('Empty cart');
  for (const item of cart.items) {
    const product = await getProduct(item.productId);
    if (product.stock < item.quantity) {
      throw new Error(`Insufficient stock for ${product.name}`);
    }
  }
  
  // Calculate totals
  let subtotal = 0;
  for (const item of cart.items) {
    const product = await getProduct(item.productId);
    subtotal += product.price * item.quantity;
  }
  const tax = subtotal * 0.1;
  const shipping = subtotal > 100 ? 0 : 10;
  const total = subtotal + tax + shipping;
  
  // Process payment
  const paymentIntent = await stripe.paymentIntents.create({
    amount: Math.round(total * 100),
    currency: 'usd',
  });
  
  // Create order
  const order = await db.orders.create({
    userId: user.id,
    items: cart.items,
    total,
    paymentIntentId: paymentIntent.id,
  });
  
  // Send confirmation
  await sendEmail(user.email, 'Order Confirmed', `Order #${order.id}`);
  
  // Update inventory
  for (const item of cart.items) {
    await db.products.update(item.productId, {
      stock: { decrement: item.quantity },
    });
  }
  
  return order;
}
```

**Refactoring**: Extract Method

```typescript
// ✅ Refactored: Each function does one thing
async function processCheckout(cart: Cart, user: User) {
  await validateCart(cart);
  const totals = await calculateTotals(cart);
  const payment = await processPayment(totals.total);
  const order = await createOrder(user, cart, totals, payment);
  await sendOrderConfirmation(user, order);
  await updateInventory(cart.items);
  return order;
}

async function validateCart(cart: Cart): Promise<void> {
  if (!cart.items.length) throw new Error('Empty cart');
  for (const item of cart.items) {
    const product = await getProduct(item.productId);
    if (product.stock < item.quantity) {
      throw new Error(`Insufficient stock for ${product.name}`);
    }
  }
}

async function calculateTotals(cart: Cart): Promise<OrderTotals> {
  const subtotal = await calculateSubtotal(cart.items);
  const tax = subtotal * 0.1;
  const shipping = subtotal > 100 ? 0 : 10;
  return { subtotal, tax, shipping, total: subtotal + tax + shipping };
}
```

**Prevention**: If you're adding a comment to separate sections, extract a function instead.

---

### Large Class

**Symptoms**:
- Class has 10+ methods
- Class has 10+ fields
- Class name includes "Manager", "Processor", "Handler" doing everything
- You can't summarize what the class does in one sentence

```typescript
// ❌ Smell: God class that does everything
class UserManager {
  // User CRUD
  createUser(data: UserInput) { /* ... */ }
  updateUser(id: string, data: UserInput) { /* ... */ }
  deleteUser(id: string) { /* ... */ }
  getUser(id: string) { /* ... */ }
  listUsers(filters: UserFilters) { /* ... */ }
  
  // Authentication
  login(email: string, password: string) { /* ... */ }
  logout(userId: string) { /* ... */ }
  resetPassword(email: string) { /* ... */ }
  verifyEmail(token: string) { /* ... */ }
  
  // Authorization
  checkPermission(userId: string, resource: string) { /* ... */ }
  assignRole(userId: string, role: string) { /* ... */ }
  
  // Profile
  updateProfile(userId: string, profile: Profile) { /* ... */ }
  uploadAvatar(userId: string, file: File) { /* ... */ }
  
  // Notifications
  sendWelcomeEmail(userId: string) { /* ... */ }
  sendPasswordResetEmail(email: string) { /* ... */ }
  
  // Analytics
  trackLogin(userId: string) { /* ... */ }
  getLoginHistory(userId: string) { /* ... */ }
}
```

**Refactoring**: Extract Class

```typescript
// ✅ Refactored: Single Responsibility
class UserRepository {
  create(data: UserInput) { /* ... */ }
  update(id: string, data: UserInput) { /* ... */ }
  delete(id: string) { /* ... */ }
  findById(id: string) { /* ... */ }
  findMany(filters: UserFilters) { /* ... */ }
}

class AuthService {
  login(email: string, password: string) { /* ... */ }
  logout(userId: string) { /* ... */ }
  resetPassword(email: string) { /* ... */ }
  verifyEmail(token: string) { /* ... */ }
}

class AuthorizationService {
  checkPermission(userId: string, resource: string) { /* ... */ }
  assignRole(userId: string, role: string) { /* ... */ }
}

class ProfileService {
  updateProfile(userId: string, profile: Profile) { /* ... */ }
  uploadAvatar(userId: string, file: File) { /* ... */ }
}

class UserNotificationService {
  sendWelcomeEmail(userId: string) { /* ... */ }
  sendPasswordResetEmail(email: string) { /* ... */ }
}
```

**Prevention**: Each class should have one reason to change.

---

### Long Parameter List

**Symptoms**:
- Function has 4+ parameters
- Parameters are often passed together
- Hard to remember parameter order
- Boolean parameters with unclear meaning

```typescript
// ❌ Smell: Too many parameters
function createReport(
  title: string,
  startDate: Date,
  endDate: Date,
  format: string,
  includeCharts: boolean,
  includeTables: boolean,
  groupBy: string,
  sortBy: string,
  sortOrder: string,
  limit: number,
  userId: string
) {
  // ...
}
```

**Refactoring**: Introduce Parameter Object

```typescript
// ✅ Refactored: Options object
interface ReportOptions {
  title: string;
  dateRange: {
    start: Date;
    end: Date;
  };
  format: 'pdf' | 'excel' | 'csv';
  includes?: {
    charts?: boolean;
    tables?: boolean;
  };
  sorting?: {
    field: string;
    order: 'asc' | 'desc';
  };
  groupBy?: string;
  limit?: number;
  userId: string;
}

function createReport(options: ReportOptions) {
  const { title, dateRange, format, includes, sorting, limit = 100 } = options;
  // ...
}
```

**Prevention**: If parameters travel together, they belong together.

---

### Data Clumps

**Symptoms**:
- Same 3+ fields appear together in multiple places
- Functions pass the same group of parameters
- Classes have fields that are always used together

```typescript
// ❌ Smell: Same fields everywhere
function calculateDistance(
  startLat: number, startLng: number,
  endLat: number, endLng: number
) { /* ... */ }

function formatAddress(
  street: string, city: string, state: string, zip: string
) { /* ... */ }

class Delivery {
  pickupStreet: string;
  pickupCity: string;
  pickupState: string;
  pickupZip: string;
  
  dropoffStreet: string;
  dropoffCity: string;
  dropoffState: string;
  dropoffZip: string;
}
```

**Refactoring**: Extract Class

```typescript
// ✅ Refactored: Create value objects
interface Coordinates {
  latitude: number;
  longitude: number;
}

interface Address {
  street: string;
  city: string;
  state: string;
  zip: string;
}

function calculateDistance(start: Coordinates, end: Coordinates) { /* ... */ }
function formatAddress(address: Address) { /* ... */ }

class Delivery {
  pickup: Address;
  dropoff: Address;
}
```

**Prevention**: When you see fields traveling together, introduce a class.

---

### Primitive Obsession

**Symptoms**:
- Using strings/numbers where a class would be clearer
- Validation logic repeated for the same concept
- Magic strings or numbers scattered in code

```typescript
// ❌ Smell: Primitives everywhere
function processOrder(
  userId: string,           // Could be UserId
  email: string,            // Could be Email
  phone: string,            // Could be PhoneNumber
  amount: number,           // Could be Money
  currency: string,         // Could be Currency
  status: string            // Could be OrderStatus
) {
  // Email validation repeated everywhere
  if (!email.includes('@')) throw new Error('Invalid email');
  
  // Currency logic scattered
  if (currency === 'USD') { /* ... */ }
  else if (currency === 'EUR') { /* ... */ }
  
  // Status checks using magic strings
  if (status === 'pending') { /* ... */ }
}
```

**Refactoring**: Replace Primitive with Object

```typescript
// ✅ Refactored: Domain types encapsulate rules
class Email {
  private constructor(private readonly value: string) {}
  
  static create(value: string): Email {
    if (!value.includes('@')) throw new Error('Invalid email');
    return new Email(value.toLowerCase());
  }
  
  toString() { return this.value; }
}

class Money {
  constructor(
    private readonly amount: number,
    private readonly currency: Currency
  ) {}
  
  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return new Money(this.amount + other.amount, this.currency);
  }
}

type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered';

function processOrder(
  userId: UserId,
  email: Email,
  amount: Money,
  status: OrderStatus
) {
  // No validation needed—types enforce rules
}
```

**Prevention**: If you validate a primitive the same way multiple times, wrap it.

---

## Object-Orientation Abusers

Incorrect or incomplete application of OO principles.

### Switch Statements

**Symptoms**:
- Same switch/if-else chain in multiple places
- Adding a new case requires changes in multiple files
- Switches based on type codes

```typescript
// ❌ Smell: Type-based switching repeated everywhere
function calculatePay(employee: Employee): number {
  switch (employee.type) {
    case 'hourly':
      return employee.hoursWorked * employee.hourlyRate;
    case 'salaried':
      return employee.annualSalary / 12;
    case 'commissioned':
      return employee.baseSalary + employee.sales * employee.commissionRate;
    default:
      throw new Error('Unknown employee type');
  }
}

function getTimeOffDays(employee: Employee): number {
  switch (employee.type) {
    case 'hourly': return 10;
    case 'salaried': return 20;
    case 'commissioned': return 15;
    default: return 0;
  }
}
```

**Refactoring**: Replace Conditional with Polymorphism

```typescript
// ✅ Refactored: Polymorphism
interface Employee {
  calculatePay(): number;
  getTimeOffDays(): number;
}

class HourlyEmployee implements Employee {
  constructor(
    private hoursWorked: number,
    private hourlyRate: number
  ) {}
  
  calculatePay() { return this.hoursWorked * this.hourlyRate; }
  getTimeOffDays() { return 10; }
}

class SalariedEmployee implements Employee {
  constructor(private annualSalary: number) {}
  
  calculatePay() { return this.annualSalary / 12; }
  getTimeOffDays() { return 20; }
}

class CommissionedEmployee implements Employee {
  constructor(
    private baseSalary: number,
    private sales: number,
    private commissionRate: number
  ) {}
  
  calculatePay() {
    return this.baseSalary + this.sales * this.commissionRate;
  }
  getTimeOffDays() { return 15; }
}
```

**Prevention**: If switches on type appear in multiple places, use polymorphism.

---

### Temporary Field

**Symptoms**:
- Fields that are only set in certain situations
- Null checks scattered throughout the class
- Fields used by only some methods

```typescript
// ❌ Smell: Fields only valid sometimes
class Order {
  items: OrderItem[];
  customer: Customer;
  
  // Only set during discount calculation
  discountPercentage?: number;
  discountReason?: string;
  discountApprover?: string;
  
  // Only set after shipping
  trackingNumber?: string;
  carrier?: string;
  estimatedDelivery?: Date;
  
  calculateTotal() {
    let total = this.items.reduce((sum, i) => sum + i.price, 0);
    // Null check because field might not exist
    if (this.discountPercentage) {
      total *= (1 - this.discountPercentage / 100);
    }
    return total;
  }
}
```

**Refactoring**: Extract Class or Introduce Null Object

```typescript
// ✅ Refactored: Separate concerns
class Order {
  items: OrderItem[];
  customer: Customer;
  discount: Discount = Discount.none();
  shipping?: ShippingInfo;
  
  calculateTotal() {
    const subtotal = this.items.reduce((sum, i) => sum + i.price, 0);
    return this.discount.applyTo(subtotal);
  }
}

class Discount {
  private constructor(
    private percentage: number,
    private reason: string,
    private approver: string | null
  ) {}
  
  static none() { return new Discount(0, '', null); }
  
  static create(percentage: number, reason: string, approver: string) {
    return new Discount(percentage, reason, approver);
  }
  
  applyTo(amount: number) {
    return amount * (1 - this.percentage / 100);
  }
}

interface ShippingInfo {
  trackingNumber: string;
  carrier: string;
  estimatedDelivery: Date;
}
```

**Prevention**: If fields are only used together, extract them to a class.

---

## Change Preventers

Code structures that make changes difficult.

### Divergent Change

**Symptoms**:
- One class is modified for multiple unrelated reasons
- Changes in different domains affect the same file
- "I need to change X, Y, and Z in this file"

```typescript
// ❌ Smell: Class changes for different reasons
class ReportGenerator {
  // Changes when report format changes
  generatePDF(data: ReportData) { /* ... */ }
  generateExcel(data: ReportData) { /* ... */ }
  generateCSV(data: ReportData) { /* ... */ }
  
  // Changes when data source changes
  fetchFromDatabase(query: string) { /* ... */ }
  fetchFromAPI(endpoint: string) { /* ... */ }
  
  // Changes when business logic changes
  calculateTotals(data: ReportData) { /* ... */ }
  applyFilters(data: ReportData) { /* ... */ }
}
```

**Refactoring**: Extract Class

```typescript
// ✅ Refactored: Separate by reason for change
class ReportFormatter {
  toPDF(data: ReportData) { /* ... */ }
  toExcel(data: ReportData) { /* ... */ }
  toCSV(data: ReportData) { /* ... */ }
}

class DataFetcher {
  fromDatabase(query: string) { /* ... */ }
  fromAPI(endpoint: string) { /* ... */ }
}

class ReportCalculator {
  calculateTotals(data: ReportData) { /* ... */ }
  applyFilters(data: ReportData) { /* ... */ }
}

class ReportGenerator {
  constructor(
    private fetcher: DataFetcher,
    private calculator: ReportCalculator,
    private formatter: ReportFormatter
  ) {}
  
  generate(source: DataSource, format: Format): Report {
    const data = this.fetcher.fetch(source);
    const processed = this.calculator.process(data);
    return this.formatter.format(processed, format);
  }
}
```

**Prevention**: Each class should have one reason to change.

---

### Shotgun Surgery

**Symptoms**:
- A single change requires editing many files
- Related code is scattered across the codebase
- Easy to miss one of the required changes

```typescript
// ❌ Smell: Adding a field requires changes everywhere
// user.ts
interface User { name: string; email: string; }

// api/users.ts
app.post('/users', (req) => {
  const { name, email } = req.body;
  // ...
});

// validation.ts
function validateUser(data: unknown) {
  if (!data.name) throw new Error('Name required');
  if (!data.email) throw new Error('Email required');
}

// database/user-repo.ts
function createUser(name: string, email: string) {
  db.query('INSERT INTO users (name, email) VALUES (?, ?)', [name, email]);
}

// Adding 'phone' requires changes in 4+ files!
```

**Refactoring**: Move Method, Inline Class

```typescript
// ✅ Refactored: Centralize related logic
// user.ts - Single source of truth
interface User {
  name: string;
  email: string;
  phone?: string;
}

const UserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  phone: z.string().optional(),
});

class UserRepository {
  create(data: User) {
    const validated = UserSchema.parse(data);
    return db.users.create(validated);
  }
}

// api/users.ts - Just orchestration
app.post('/users', async (req) => {
  const user = await userRepository.create(req.body);
  return user;
});
```

**Prevention**: Keep related behavior together.

---

### Feature Envy

**Symptoms**:
- A method uses more features of another class than its own
- Lots of getter calls on other objects
- Logic that should belong to the data it operates on

```typescript
// ❌ Smell: OrderPrinter is too interested in Order
class OrderPrinter {
  print(order: Order) {
    console.log(`Order: ${order.getId()}`);
    console.log(`Customer: ${order.getCustomer().getName()}`);
    console.log(`Address: ${order.getCustomer().getAddress().getFullAddress()}`);
    
    let total = 0;
    for (const item of order.getItems()) {
      const price = item.getProduct().getPrice();
      const qty = item.getQuantity();
      const discount = item.getProduct().getDiscount();
      const lineTotal = price * qty * (1 - discount);
      total += lineTotal;
      console.log(`${item.getProduct().getName()}: $${lineTotal}`);
    }
    
    console.log(`Total: $${total}`);
  }
}
```

**Refactoring**: Move Method

```typescript
// ✅ Refactored: Move logic to where data lives
class Order {
  getFormattedSummary(): string {
    return [
      `Order: ${this.id}`,
      `Customer: ${this.customer.name}`,
      `Address: ${this.customer.address.format()}`,
      ...this.items.map(item => item.format()),
      `Total: $${this.calculateTotal()}`,
    ].join('\n');
  }
  
  calculateTotal(): number {
    return this.items.reduce((sum, item) => sum + item.calculateLineTotal(), 0);
  }
}

class OrderItem {
  calculateLineTotal(): number {
    return this.product.price * this.quantity * (1 - this.product.discount);
  }
  
  format(): string {
    return `${this.product.name}: $${this.calculateLineTotal()}`;
  }
}

class OrderPrinter {
  print(order: Order) {
    console.log(order.getFormattedSummary());
  }
}
```

**Prevention**: Put behavior with the data it needs.

---

## Dispensables

Code that serves no purpose and should be removed.

### Dead Code

**Symptoms**:
- Unreachable code after return/throw
- Unused variables, parameters, or functions
- Commented-out code
- Obsolete feature flags

```typescript
// ❌ Smell: Code that's never executed
function processPayment(amount: number) {
  if (amount <= 0) {
    throw new Error('Invalid amount');
    console.log('This never runs'); // Dead code
  }
  
  const result = charge(amount);
  return result;
  
  // Everything below is dead code
  sendReceipt(result);
  updateAnalytics(result);
}

// Unused function
function legacyPaymentProcessor() {
  // Old code nobody uses
}

// Unused variable
const FEATURE_FLAG_OLD = false;
```

**Refactoring**: Remove Dead Code

```typescript
// ✅ Refactored: Delete it
function processPayment(amount: number) {
  if (amount <= 0) {
    throw new Error('Invalid amount');
  }
  
  const result = charge(amount);
  sendReceipt(result);
  updateAnalytics(result);
  return result;
}
```

**Prevention**: Use your IDE's "find unused" feature regularly.

---

### Speculative Generality

**Symptoms**:
- Abstract classes with only one implementation
- Parameters or methods that are never used
- "We might need this someday" code
- Complex framework for simple problem

```typescript
// ❌ Smell: Over-engineered for imaginary requirements
interface PaymentProcessor {
  process(payment: Payment): Promise<Result>;
  refund(paymentId: string): Promise<Result>;
  void(paymentId: string): Promise<Result>;
  partialRefund(paymentId: string, amount: number): Promise<Result>;
  recurring(subscription: Subscription): Promise<Result>;
}

// Only implementation
class StripeProcessor implements PaymentProcessor {
  // We only use process() and refund()
  // Other methods throw "not implemented"
  process(payment: Payment) { /* ... */ }
  refund(paymentId: string) { /* ... */ }
  void() { throw new Error('Not implemented'); }
  partialRefund() { throw new Error('Not implemented'); }
  recurring() { throw new Error('Not implemented'); }
}
```

**Refactoring**: Collapse Hierarchy, Remove Parameter

```typescript
// ✅ Refactored: Only what's actually needed
class PaymentService {
  constructor(private stripe: Stripe) {}
  
  async charge(amount: number, customer: string) {
    return this.stripe.charges.create({ amount, customer });
  }
  
  async refund(chargeId: string) {
    return this.stripe.refunds.create({ charge: chargeId });
  }
}
```

**Prevention**: YAGNI—You Aren't Gonna Need It.

---

### Duplicate Code

**Symptoms**:
- Same code structure in multiple places
- Copy-pasted code with minor variations
- Parallel inheritance hierarchies

```typescript
// ❌ Smell: Same logic in multiple places
class AdminController {
  async getUsers(req: Request) {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const offset = (page - 1) * limit;
    
    const users = await db.users.findMany({ skip: offset, take: limit });
    const total = await db.users.count();
    
    return {
      data: users,
      meta: { page, limit, total, pages: Math.ceil(total / limit) }
    };
  }
}

class ProductController {
  async getProducts(req: Request) {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const offset = (page - 1) * limit;
    
    const products = await db.products.findMany({ skip: offset, take: limit });
    const total = await db.products.count();
    
    return {
      data: products,
      meta: { page, limit, total, pages: Math.ceil(total / limit) }
    };
  }
}
```

**Refactoring**: Extract Function, Extract Class

```typescript
// ✅ Refactored: Shared pagination logic
interface PaginationParams {
  page: number;
  limit: number;
}

function parsePagination(query: Record<string, string>): PaginationParams {
  return {
    page: parseInt(query.page) || 1,
    limit: parseInt(query.limit) || 10,
  };
}

async function paginate<T>(
  query: { findMany: Function; count: Function },
  params: PaginationParams
) {
  const { page, limit } = params;
  const offset = (page - 1) * limit;
  
  const [data, total] = await Promise.all([
    query.findMany({ skip: offset, take: limit }),
    query.count(),
  ]);
  
  return {
    data,
    meta: { page, limit, total, pages: Math.ceil(total / limit) }
  };
}

class AdminController {
  async getUsers(req: Request) {
    return paginate(db.users, parsePagination(req.query));
  }
}

class ProductController {
  async getProducts(req: Request) {
    return paginate(db.products, parsePagination(req.query));
  }
}
```

**Prevention**: If you copy-paste, extract immediately.

---

## Couplers

Code with excessive coupling between classes.

### Message Chains

**Symptoms**:
- Long chains of method calls: `a.getB().getC().getD().doSomething()`
- Client depends on navigation structure
- Changes to intermediate objects break clients

```typescript
// ❌ Smell: Reaching through objects
function getManagerEmail(employee: Employee): string {
  return employee
    .getDepartment()
    .getManager()
    .getContactInfo()
    .getEmail()
    .toLowerCase();
}

function sendReport(order: Order) {
  const warehouse = order
    .getShipment()
    .getRoute()
    .getDestination()
    .getWarehouse();
    
  warehouse.receive(order);
}
```

**Refactoring**: Hide Delegate

```typescript
// ✅ Refactored: Ask, don't navigate
class Employee {
  getManagerEmail(): string {
    return this.department.getManagerEmail();
  }
}

class Department {
  getManagerEmail(): string {
    return this.manager.email.toLowerCase();
  }
}

// Client is simple
function getManagerEmail(employee: Employee): string {
  return employee.getManagerEmail();
}

// Or use delegation
class Order {
  getDestinationWarehouse(): Warehouse {
    return this.shipment.getDestinationWarehouse();
  }
}
```

**Prevention**: Follow the Law of Demeter—only talk to immediate friends.

---

### Middle Man

**Symptoms**:
- Class mostly delegates to another class
- No added value, just passing through
- Interface mirrors another class

```typescript
// ❌ Smell: Pure delegation
class PersonWrapper {
  private person: Person;
  
  getName() { return this.person.getName(); }
  setName(name: string) { this.person.setName(name); }
  getAge() { return this.person.getAge(); }
  setAge(age: number) { this.person.setAge(age); }
  getAddress() { return this.person.getAddress(); }
  setAddress(addr: Address) { this.person.setAddress(addr); }
  // Every method just delegates
}
```

**Refactoring**: Remove Middle Man

```typescript
// ✅ Refactored: Use the class directly
// Delete PersonWrapper, use Person directly

// If some delegation is valuable, keep only that:
class PersonView {
  constructor(private person: Person) {}
  
  // Only expose what's needed, add value
  getDisplayName(): string {
    return `${this.person.getName()} (${this.person.getAge()})`;
  }
}
```

**Prevention**: Only add indirection when it provides value.

---

## Quick Reference

| Category | Smell | Fix |
|----------|-------|-----|
| **Bloaters** | Long Method | Extract Method |
| | Large Class | Extract Class |
| | Long Parameter List | Parameter Object |
| | Data Clumps | Extract Class |
| | Primitive Obsession | Replace with Object |
| **OO Abusers** | Switch Statements | Polymorphism |
| | Temporary Field | Extract Class |
| **Change Preventers** | Divergent Change | Extract Class |
| | Shotgun Surgery | Move Method |
| | Feature Envy | Move Method |
| **Dispensables** | Dead Code | Delete it |
| | Speculative Generality | Delete it |
| | Duplicate Code | Extract |
| **Couplers** | Message Chains | Hide Delegate |
| | Middle Man | Remove it |
