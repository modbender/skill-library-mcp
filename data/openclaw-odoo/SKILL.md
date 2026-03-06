---
name: odoo
description: Full-featured Odoo 17/18/19 ERP connector for OpenClaw — Sales, CRM, Purchase, Inventory, Projects, HR, Fleet, Manufacturing (80+ operations, TypeScript plugin, XML-RPC integration).
repository: https://github.com/tuanle96/openclaw-odoo
---

# Odoo ERP Connector

Full-featured Odoo 17/18/19 ERP integration for OpenClaw. Control your entire business via natural language chat commands.

**📦 Full Source Code:** https://github.com/tuanle96/openclaw-odoo

## Quick Install

```bash
npx clawhub install openclaw-odoo
```

## Overview

The Odoo ERP Connector bridges OpenClaw and Odoo 17/18/19, enabling autonomous, chat-driven control over 153+ business modules including:
- Sales & CRM
- Purchasing & Inventory  
- Invoicing & Accounting
- Projects & Task Management
- Human Resources
- Fleet Management
- Manufacturing (MRP)
- Calendar & Events
- eCommerce

All operations use **smart actions** that handle fuzzy matching and auto-creation workflows.

## Capabilities

### Sales & CRM
- Create quotations with dynamic line items
- Manage sales orders (draft → confirmed → done)
- Search and filter orders by status, customer, date range
- Create and qualify leads and opportunities
- Move leads through CRM pipeline stages
- View full sales pipeline with revenue forecasting

### Purchasing
- Create purchase orders from vendors
- Manage PO status (draft → purchase → received)
- Receive and validate goods
- Search and filter POs by vendor, status, date
- Track purchase history and vendor performance

### Inventory & Products
- Create products (consumables, stockable, services)
- Query stock levels and availability
- Set reorder points and receive low-stock alerts
- Search products by name, code, or category
- Track stock movements and valuations

### Invoicing & Accounting
- Create and post customer invoices
- Manage payment terms and schedules
- Query unpaid and overdue invoices
- Search by customer, date range, or amount
- Track invoice status (draft → posted → paid)

### Projects & Tasks
- Create projects and organize by team/status
- Create tasks with priority, dates, and assignments
- Log timesheets and track project hours
- Search and filter tasks by project, status, assignee
- Manage project stages and closure

### Human Resources
- Create employees and departments
- Manage job titles and work schedules
- Process expense reports and reimbursements
- Search employees by name, department, job
- Track leave requests and attendance

### Fleet Management
- Create and track vehicles
- Log odometer readings and service records
- Track maintenance schedules and costs
- Search fleet by license plate, status, brand
- Generate fleet reports

### Manufacturing (MRP)
- Create Bills of Materials (BOMs)
- Manage manufacturing orders (MOs)
- Track component requirements and production status
- Search MOs by product or status
- Link BOMs to product variants

### Calendar & Events
- Create meetings and events with attendees
- Set reminders and locations
- Search events by date range or attendee
- Track calendar availability

### eCommerce
- Publish products to website
- View website orders and customer activity
- Manage product visibility and pricing

## Command Examples

### Sales
- "Create a quotation for Acme Corp with 10 Widgets at $50 each"
- "Confirm sales order SO00042"
- "Show me all draft quotations from the past week"
- "What's the total revenue from completed orders this month?"
- "Create a quote for Rocky with product Rock"

### CRM
- "Create a lead for Rocky, email rocky@example.com, potential $50k deal"
- "Move lead #47 to Qualified stage"
- "Show me the sales pipeline with all open opportunities"
- "What leads are at proposal stage?"
- "Create an opportunity for Acme with $100k expected value"

### Purchasing
- "Create a PO for 500 widgets from Supplier ABC"
- "Confirm purchase order PO00123"
- "Show all pending purchase orders"
- "Get me the vendor history for ABC Supplies"
- "What's on order that's overdue?"

### Inventory & Products
- "Create a new product: TestWidget, $25 price, min stock 10"
- "Show products with stock below 20 units"
- "What's the stock level for Widget X?"
- "Search for all consumable products"
- "Set reorder point for Product Y to 50 units"

### Invoicing
- "Create an invoice for Acme Corp with 5 units at $50 each"
- "Show me unpaid invoices"
- "What invoices are overdue?"
- "Post invoice INV-001"
- "Send a reminder for invoice INV-002"

### Projects & Tasks
- "Create a project called Website Redesign"
- "Create a task 'Fix login button' in Website Redesign project"
- "Show me all tasks assigned to me"
- "Log 3 hours of work on task #42"
- "What's the status of the Website Redesign project?"

### HR
- "Create employee John Smith, job title Developer"
- "Create department Engineering"
- "Show me all employees in Engineering"
- "Submit expense report for $45.99"
- "What are the pending leave requests?"

### Fleet
- "Create vehicle: Tesla Model 3, license plate TESLA-001"
- "Log odometer reading: 50,000 miles for vehicle #1"
- "Show all vehicles with service due"
- "What's the maintenance cost for this month?"
- "Search for blue vehicles"

### Manufacturing
- "Create BOM: Widget contains 3 Components A and 2 Components B"
- "Create manufacturing order: produce 50 Widgets"
- "Confirm production order #1"
- "What's the status of MO-001?"
- "Show all in-progress manufacturing orders"

### Calendar
- "Create meeting: Team Standup, tomorrow at 10am, 1 hour"
- "Show me my meetings for next week"
- "What events do I have on the 15th?"
- "Schedule a 2-hour planning session with the team"

### eCommerce
- "Publish Widget X to the website"
- "Show me website orders from this week"
- "What's my website revenue?"

## Smart Actions

The connector handles fuzzy/incomplete requests with intelligent find-or-create logic.

### How Smart Actions Work

**Example:** "Create quotation for Rocky with product Rock"

The system:
1. **Searches** for a customer named "Rocky" (case-insensitive, `ilike` matching)
2. **If not found**: Creates a new customer "Rocky" (auto-company flag)
3. **Searches** for product "Rock"
4. **If not found**: Creates a basic product "Rock" (consumable type, default price $0)
5. **Creates** the quotation, linking both the found/created customer and product
6. **Reports** what was found vs. created:
   - "Created quotation QT-001 for new customer Rocky with 1 × Rock at $0.00"

This pattern applies across all smart actions:
- `create_quotation` — customer + products
- `create_invoice` — customer + products
- `create_purchase` — vendor + products
- `create_lead` — partner (optional)
- `create_task` — project + task
- `create_employee` — department
- `create_event` — event only (no dependencies)

### Benefits

- **Fuzzy matching**: Searches are case-insensitive and forgiving
- **Auto-creation**: Missing dependencies are created automatically
- **Transparency**: Each response explains what was created vs. found
- **No IDs needed**: Use names instead of Odoo IDs
- **Batch operations**: Create multiple related records in one call

## Architecture

### Core Components

**OdooClient** — Low-level XML-RPC wrapper
- Connects to Odoo 17/18/19 instance
- Handles authentication via API key
- Provides `search()`, `searchRead()`, `create()`, `write()`, `unlink()` methods
- Built-in retry logic and error handling

**Model Ops Classes** — Business logic for each module
- `PartnerOps` — Customers/suppliers
- `SaleOrderOps` — Quotations and sales orders
- `InvoiceOps` — Customer invoices
- `InventoryOps` — Products and stock
- `CRMOps` — Leads and opportunities
- `PurchaseOrderOps` — POs and vendors
- `ProjectOps` — Projects and tasks
- `HROps` — Employees, departments, expenses
- `ManufacturingOps` — BOMs and MOs
- `CalendarOps` — Events and meetings
- `FleetOps` — Vehicles and odometer
- `EcommerceOps` — Website orders and products

**SmartActionHandler** — High-level find-or-create workflows
- Wraps all Ops classes
- Implements find-or-create workflows
- Fuzzy name matching (case-insensitive)
- Multi-step transaction orchestration
- Detailed response summaries

### Field Handling

The connector auto-detects required vs. optional fields:
- **Implicit defaults**: Fields with Odoo defaults (e.g., state) are omitted
- **Smart creation**: Auto-fills reasonable defaults for optional fields
- **Error reporting**: Missing required fields raise clear `OdooError` with field name

## Configuration

### Plugin Config (openclaw.plugin.json)

```json
{
  "url": "http://localhost:8069",
  "db": "your_database",
  "username": "api_user@yourcompany.com",
  "apiKey": "your_api_key_from_odoo_preferences",
  "timeout": 60,
  "maxRetries": 3,
  "pollInterval": 60,
  "logLevel": "INFO",
  "webhookPort": 8070,
  "webhookSecret": ""
}
```

Config keys are camelCase only.

### Getting Your API Key

1. Log in to your Odoo instance
2. Go to **Settings** → **Users & Companies** → **Users**
3. Open your user record
4. Scroll to **Access Tokens**
5. Click **Generate Token**
6. Copy the token into your config

### Environment Variables

Alternatively, set in `.env`:

```
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=api_user@yourcompany.com
ODOO_API_KEY=your_api_key
```

The client auto-loads from `.env` if plugin config is missing.

## TypeScript API

### Basic Usage

```typescript
import { OdooSession } from "./odoo/session";
import { loadOdooConfig } from "./odoo/config";
import { SmartActionHandler } from "./odoo/smart-actions";

// Load config from plugin config or env
const { config } = loadOdooConfig({ url: "...", db: "...", username: "...", apiKey: "..." });
const session = await OdooSession.connect(config);

// Test connection
const status = await session.testConnection();
console.log(`Connected to Odoo ${status.server_version}`);

// Use smart actions for natural workflows
const smart = new SmartActionHandler(session);

// Create a quotation with fuzzy partner and product matching
const result = await smart.smartCreateQuotation(
  "Rocky",
  [{ name: "Rock", quantity: 5, price_unit: 19.99 }],
  { notes: "Fuzzy match quotation" }
);
console.log(result.summary);
// Output: "Created quotation QT-001 for new customer Rocky with 1 × Rock at $19.99"
```

### Smart Actions API

```typescript
// Find-or-create a customer
const partnerResult = await smart.findOrCreatePartner("Acme Corp", {
  isCompany: true,
  defaults: { city: "New York" }
});
const partner = partnerResult.partner;
const created = partnerResult.created;

// Find-or-create a product
const productResult = await smart.findOrCreateProduct("Widget X", {
  list_price: 49.99,
  type: "consu"
});
const product = productResult.product;

// Smart quotation (auto-creates customer & products)
const orderResult = await smart.smartCreateQuotation(
  "Rocky",
  [
    { name: "Product A", quantity: 10 },
    { name: "Product B", quantity: 5, price_unit: 25.0 }
  ],
  { notes: "Created via smart action" }
);
const order = orderResult.order;
console.log(`Order ${order.name} created`);

// Smart lead creation
const leadResult = await smart.smartCreateLead("New Prospect", {
  contactName: "John Doe",
  email: "john@prospect.com",
  expectedRevenue: 50000.0
});

// Smart task creation (auto-creates project if needed)
const taskResult = await smart.smartCreateTask(
  "Website Redesign",
  "Fix homepage",
  { description: "Update hero section" }
);

// Smart employee creation (auto-creates department if needed)
const empResult = await smart.smartCreateEmployee("Jane Smith", {
  jobTitle: "Developer",
  departmentName: "Engineering"
});

// Smart event creation
const eventResult = await smart.smartCreateEvent(
  "Team Standup",
  "2026-03-01T10:00:00",
  { location: "Room A", attendeeNames: ["Alice", "Bob"] }
);
```

### Low-Level Client API

```typescript
// Search and read records
const partners = await client.searchRead(
  "res.partner",
  [["is_company", "=", true]],
  ["name", "email"],
  { limit: 10 }
);

// Create a record
const id = await client.create("sale.order", {
  partner_id: 42,
  order_line: [[0, 0, { product_id: 7, product_uom_qty: 10, price_unit: 49.99 }]]
});

// Update a record
await client.write("sale.order", id, { note: "Updated via API" });

// Delete a record
await client.unlink("sale.order", [id]);

// Execute workflow actions
await client.execute("sale.order", "action_confirm", [[id]]);

// Get field definitions
const fields = await client.fieldsGet("product.template");
```

## Error Handling

The connector uses typed error classes:

```typescript
import {
  OdooError,
  OdooAuthenticationError,
  OdooRecordNotFoundError,
  OdooAccessError,
  OdooValidationError,
  OdooConnectionError
} from "./odoo/errors";

try {
  const result = await smart.smartCreateQuotation("Acme", [{ name: "Widget" }]);
} catch (e) {
  if (e instanceof OdooAuthenticationError) {
    console.error(`Authentication failed: ${e.message}`);
  } else if (e instanceof OdooRecordNotFoundError) {
    console.error(`Record not found: ${e.message}`);
  } else if (e instanceof OdooAccessError) {
    console.error(`Permission denied: ${e.message}`);
  } else if (e instanceof OdooValidationError) {
    console.error(`Validation error: ${e.message}`);
  } else if (e instanceof OdooConnectionError) {
    console.error(`Connection error: ${e.message}`);
  } else if (e instanceof OdooError) {
    console.error(`Odoo error: ${e.message}`);
  }
}
```

## OpenClaw Tools

The plugin registers **8 tools** accessible via natural language:

| Tool | Description |
|------|-------------|
| `odoo_health` | Config sanity check (no network) |
| `odoo_test_connection` | Live XML-RPC connectivity check |
| `odoo_search` | Search & read records with domain filters |
| `odoo_create` | Create records on any model |
| `odoo_update` | Update existing records |
| `odoo_delete` | Delete records |
| `odoo_workflow` | Execute model methods (confirm/cancel/post) |
| `odoo_smart_action` | High-level find-or-create workflows |

## Examples in OpenClaw

### Natural Language Sales Order

```
User: "Create a quote for Acme Corp with 10 Widgets at $50 each"

OpenClaw → odoo_smart_action (create_quotation):
  1. Search for customer "Acme Corp"
  2. Search for product "Widgets"
  3. Create quotation with both
  4. Return summary

Result: "✅ Created quotation QT-001 for Acme Corp with 10 × Widgets at $50"
```

### Pipeline Status Check

```
User: "Show me the sales pipeline"

OpenClaw → odoo_search (crm.lead):
  - Query all leads/opportunities
  - Group by stage
  - Calculate total revenue by stage
  - Return formatted summary

Result: "Qualified: $50k | Proposal: $100k | Negotiation: $75k | Total: $225k"
```

### Inventory Alert

```
User: "What products are low on stock?"

OpenClaw → odoo_search (product.template):
  - Query products with stock < reorder point
  - List each product, stock level, reorder point
  - Suggest PO quantities

Result: "Widget X: 5 on hand (min 20) | Component Y: 0 on hand (min 10)"
```

## Development

### Project Structure

```
openclaw-odoo/
├── plugin/
│   ├── openclaw.plugin.json    # Plugin manifest + config schema
│   ├── package.json            # @openclaw/openclaw-odoo@2.0.0
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts            # Entry point (registers 8 tools)
│   │   ├── odoo/               # Core: client, config, errors, retry
│   │   │   ├── client.ts       # OdooClient (XML-RPC wrapper)
│   │   │   ├── config.ts       # Configuration loader
│   │   │   ├── errors.ts       # Typed error classes
│   │   │   ├── retry.ts        # Retry logic
│   │   │   ├── smart-actions.ts # SmartActionHandler
│   │   │   └── models/         # 12 model operation classes
│   │   ├── tools/              # 8 OpenClaw tools
│   │   ├── services/           # Poller + webhook
│   │   ├── openclaw/           # OpenClaw API helpers + integration
│   │   └── utils/              # Validators + formatting
│   ├── tests/                  # 18 tests (Vitest)
│   ├── skills/odoo/SKILL.md    # This file (bundled AI context)
│   └── dist/                   # Compiled output (CommonJS)
├── README.md                   # User setup guide
├── CHANGELOG.md                # Version history
├── RELEASE.md                  # Release plan
├── GAP_ANALYSIS.md             # Multi-version compatibility audit
└── odoo-src/                   # Odoo source for analysis
```

### Running Tests

```bash
cd plugin
pnpm install
pnpm build          # TS → dist/ (CommonJS)
pnpm run typecheck  # tsc --noEmit (strict)
pnpm test           # vitest run (18 tests)
```

### Adding a New Smart Action

1. Implement the method in `SmartActionHandler` class (in `src/odoo/smart-actions.ts`)
2. Use `findOrCreatePartner()` / `findOrCreateProduct()` primitives for dependencies
3. Return an object with `summary`, the main record, and creation details
4. Add the action to the `ActionSchema` union in `src/tools/odoo-smart-action.ts`
5. Add a case in the `switch` statement to route the action
6. Add test in `tests/`

Example:

```typescript
async smartCreateInvoice(
  customerName: string,
  lines: Array<Record<string, unknown>>,
  options: { invoiceDate?: string; extra?: Record<string, unknown> } = {},
): Promise<Record<string, unknown>> {
  // Find or create customer
  const customerResult = await this.findOrCreatePartner(customerName);
  const customer = customerResult.partner;

  // Find or create products
  const products = [];
  for (const line of lines) {
    const prodResult = await this.findOrCreateProduct(line.name as string, line);
    products.push(prodResult);
  }

  // Create invoice with resolved IDs
  const invoiceId = await this.client.create("account.move", {
    partner_id: customer.id,
    move_type: "out_invoice",
    invoice_date: options.invoiceDate,
    invoice_line_ids: products.map((p, i) => [
      0, 0, {
        product_id: p.product.id,
        quantity: (lines[i] as any).quantity ?? 1,
        price_unit: (lines[i] as any).price_unit ?? 0,
      },
    ]),
    ...options.extra,
  });

  return {
    summary: `Created invoice for ${customer.name}`,
    invoice: { id: invoiceId },
    customer: customerResult,
    products,
  };
}
```

## Limits & Constraints

- **Search limit**: 100 records by default (configurable)
- **Timeout**: 60 seconds per request (configurable)
- **Retries**: 3 automatic retries on network failure
- **Concurrency**: Single-threaded; queue requests if needed
- **Rate limiting**: Follow your Odoo instance's API limits

## Troubleshooting

### Connection Issues
- Verify `url`, `db`, `username`, `apiKey` in config
- Check Odoo server is running: `http://your-odoo-url/web`
- Ensure API key is generated in Odoo user settings
- Check network connectivity and firewall rules

### Authentication Errors
- Regenerate API key in Odoo
- Verify username (email format)
- Check that the user has API access enabled
- Ensure database name matches exactly

### Missing Field Errors
- Field names must match Odoo version exactly (e.g., `product_tmpl_id`, not `product_id`)
- Some fields are read-only in Odoo (state, computed fields)
- Check Odoo model definition: Settings → Technical → Database Structure → Models

### Smart Action Issues
- Fuzzy matching is case-insensitive but searches only the `name` field
- For exact matching, use `odoo_search` tool with `id` directly
- If a name exists in multiple records, the first match is used

### Performance
- Large searches (limit > 100) may timeout
- Use date range filters: `date_from`, `date_to`
- Consider batch operations for bulk data

## License & Support

This connector is part of the OpenClaw project. For issues, questions, or contributions, visit [github.com/tuanle96/openclaw-odoo](https://github.com/tuanle96/openclaw-odoo).

---

**Last Updated:** 2026-02-23  
**Odoo Versions:** 17, 18, 19  
**Runtime:** Node.js (TypeScript)  
**Status:** Production Ready
