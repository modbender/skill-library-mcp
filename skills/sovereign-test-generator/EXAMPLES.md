# Sovereign Test Generator -- Examples

Real-world examples showing how the test generator analyzes code and produces complete, runnable test suites.

---

## Example 1: Generate tests for an Express.js API endpoint

### Input -- Express.js Route Handler

```javascript
// routes/tasks.js
const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/auth');
const TaskService = require('../services/TaskService');
const { body, validationResult } = require('express-validator');

router.post(
  '/',
  authenticate,
  [
    body('title').trim().notEmpty().withMessage('Title is required'),
    body('title').isLength({ max: 200 }).withMessage('Title must be 200 characters or less'),
    body('description').optional().trim().isLength({ max: 5000 }),
    body('priority').optional().isIn(['low', 'medium', 'high']).withMessage('Invalid priority'),
    body('dueDate').optional().isISO8601().withMessage('Due date must be a valid ISO 8601 date'),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const task = await TaskService.create({
        ...req.body,
        userId: req.user.id,
      });
      res.status(201).json({ task });
    } catch (error) {
      if (error.code === 'TASK_LIMIT_REACHED') {
        return res.status(429).json({ error: 'Task limit reached. Upgrade to create more tasks.' });
      }
      if (error.code === 'INVALID_DUE_DATE') {
        return res.status(400).json({ error: 'Due date must be in the future.' });
      }
      console.error('Failed to create task:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

router.get('/:id', authenticate, async (req, res) => {
  try {
    const task = await TaskService.findById(req.params.id, req.user.id);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.json({ task });
  } catch (error) {
    console.error('Failed to fetch task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/:id', authenticate, async (req, res) => {
  try {
    const deleted = await TaskService.deleteById(req.params.id, req.user.id);
    if (!deleted) {
      return res.status(404).json({ error: 'Task not found' });
    }
    res.status(204).send();
  } catch (error) {
    console.error('Failed to delete task:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
```

### Prompt

> Generate comprehensive Jest tests for this Express.js task API. Cover all endpoints, validation, error handling, and edge cases.

### Generated Output -- `__tests__/routes/tasks.test.js`

```javascript
const request = require('supertest');
const express = require('express');
const TaskService = require('../../services/TaskService');

// Mock TaskService before importing routes
jest.mock('../../services/TaskService');

// Mock authentication middleware
jest.mock('../../middleware/auth', () => ({
  authenticate: (req, res, next) => {
    if (req.headers.authorization === 'Bearer valid-token') {
      req.user = { id: 'user-123', email: 'test@example.com' };
      return next();
    }
    return res.status(401).json({ error: 'Unauthorized' });
  },
}));

const taskRoutes = require('../../routes/tasks');

// Build test app
function createApp() {
  const app = express();
  app.use(express.json());
  app.use('/tasks', taskRoutes);
  return app;
}

describe('Task Routes', () => {
  let app;

  beforeAll(() => {
    app = createApp();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ============================================================
  // POST /tasks -- Create Task
  // ============================================================
  describe('POST /tasks', () => {
    const validTask = {
      title: 'Write unit tests',
      description: 'Cover all edge cases for the task API',
      priority: 'high',
      dueDate: '2026-12-31T23:59:59Z',
    };

    const authHeader = { Authorization: 'Bearer valid-token' };

    describe('successful creation', () => {
      it('returns 201 with the created task', async () => {
        const createdTask = {
          id: 'task-1',
          ...validTask,
          userId: 'user-123',
          createdAt: '2026-02-23T00:00:00Z',
        };
        TaskService.create.mockResolvedValue(createdTask);

        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send(validTask)
          .expect(201);

        expect(response.body.task).toEqual(createdTask);
        expect(TaskService.create).toHaveBeenCalledWith({
          ...validTask,
          userId: 'user-123',
        });
      });

      it('creates task with only required fields', async () => {
        const minimalTask = { title: 'Minimal task' };
        TaskService.create.mockResolvedValue({ id: 'task-2', ...minimalTask, userId: 'user-123' });

        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send(minimalTask)
          .expect(201);

        expect(response.body.task.title).toBe('Minimal task');
      });

      it('trims whitespace from title', async () => {
        TaskService.create.mockResolvedValue({ id: 'task-3', title: 'Trimmed', userId: 'user-123' });

        await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: '  Trimmed  ' })
          .expect(201);

        expect(TaskService.create).toHaveBeenCalledWith(
          expect.objectContaining({ title: 'Trimmed' })
        );
      });
    });

    describe('authentication', () => {
      it('returns 401 when no auth header is provided', async () => {
        await request(app)
          .post('/tasks')
          .send(validTask)
          .expect(401);

        expect(TaskService.create).not.toHaveBeenCalled();
      });

      it('returns 401 with invalid token', async () => {
        await request(app)
          .post('/tasks')
          .set({ Authorization: 'Bearer invalid-token' })
          .send(validTask)
          .expect(401);
      });
    });

    describe('validation errors', () => {
      it('returns 400 when title is missing', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ description: 'No title' })
          .expect(400);

        expect(response.body.errors).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ msg: 'Title is required' }),
          ])
        );
      });

      it('returns 400 when title is empty string', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: '' })
          .expect(400);

        expect(response.body.errors).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ msg: 'Title is required' }),
          ])
        );
      });

      it('returns 400 when title is only whitespace', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: '   ' })
          .expect(400);

        expect(response.body.errors).toBeDefined();
      });

      it('returns 400 when title exceeds 200 characters', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: 'a'.repeat(201) })
          .expect(400);

        expect(response.body.errors).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ msg: 'Title must be 200 characters or less' }),
          ])
        );
      });

      it('accepts title at exactly 200 characters', async () => {
        TaskService.create.mockResolvedValue({ id: 'task-4', title: 'a'.repeat(200) });

        await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: 'a'.repeat(200) })
          .expect(201);
      });

      it('returns 400 for invalid priority value', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: 'Test', priority: 'urgent' })
          .expect(400);

        expect(response.body.errors).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ msg: 'Invalid priority' }),
          ])
        );
      });

      it('accepts all valid priority values', async () => {
        for (const priority of ['low', 'medium', 'high']) {
          TaskService.create.mockResolvedValue({ id: `task-${priority}`, title: 'Test', priority });

          await request(app)
            .post('/tasks')
            .set(authHeader)
            .send({ title: 'Test', priority })
            .expect(201);
        }
      });

      it('returns 400 for invalid due date format', async () => {
        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ title: 'Test', dueDate: 'next tuesday' })
          .expect(400);

        expect(response.body.errors).toEqual(
          expect.arrayContaining([
            expect.objectContaining({ msg: 'Due date must be a valid ISO 8601 date' }),
          ])
        );
      });
    });

    describe('service errors', () => {
      it('returns 429 when task limit is reached', async () => {
        const error = new Error('Task limit reached');
        error.code = 'TASK_LIMIT_REACHED';
        TaskService.create.mockRejectedValue(error);

        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send(validTask)
          .expect(429);

        expect(response.body.error).toContain('Task limit reached');
      });

      it('returns 400 when due date is in the past', async () => {
        const error = new Error('Invalid due date');
        error.code = 'INVALID_DUE_DATE';
        TaskService.create.mockRejectedValue(error);

        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send({ ...validTask, dueDate: '2020-01-01T00:00:00Z' })
          .expect(400);

        expect(response.body.error).toContain('Due date must be in the future');
      });

      it('returns 500 for unexpected service errors', async () => {
        TaskService.create.mockRejectedValue(new Error('Database connection lost'));

        const response = await request(app)
          .post('/tasks')
          .set(authHeader)
          .send(validTask)
          .expect(500);

        expect(response.body.error).toBe('Internal server error');
        // Verify sensitive error details are NOT leaked
        expect(response.body.error).not.toContain('Database');
      });
    });
  });

  // ============================================================
  // GET /tasks/:id -- Get Task
  // ============================================================
  describe('GET /tasks/:id', () => {
    const authHeader = { Authorization: 'Bearer valid-token' };

    it('returns 200 with the task when found', async () => {
      const task = { id: 'task-1', title: 'Test', userId: 'user-123' };
      TaskService.findById.mockResolvedValue(task);

      const response = await request(app)
        .get('/tasks/task-1')
        .set(authHeader)
        .expect(200);

      expect(response.body.task).toEqual(task);
      expect(TaskService.findById).toHaveBeenCalledWith('task-1', 'user-123');
    });

    it('returns 404 when task does not exist', async () => {
      TaskService.findById.mockResolvedValue(null);

      const response = await request(app)
        .get('/tasks/nonexistent')
        .set(authHeader)
        .expect(404);

      expect(response.body.error).toBe('Task not found');
    });

    it('passes user ID to service to enforce ownership', async () => {
      TaskService.findById.mockResolvedValue(null);

      await request(app)
        .get('/tasks/task-1')
        .set(authHeader)
        .expect(404);

      // Verify the service is called with both task ID and user ID
      expect(TaskService.findById).toHaveBeenCalledWith('task-1', 'user-123');
    });

    it('returns 401 without authentication', async () => {
      await request(app)
        .get('/tasks/task-1')
        .expect(401);
    });

    it('returns 500 when service throws unexpected error', async () => {
      TaskService.findById.mockRejectedValue(new Error('Connection refused'));

      const response = await request(app)
        .get('/tasks/task-1')
        .set(authHeader)
        .expect(500);

      expect(response.body.error).toBe('Internal server error');
    });
  });

  // ============================================================
  // DELETE /tasks/:id -- Delete Task
  // ============================================================
  describe('DELETE /tasks/:id', () => {
    const authHeader = { Authorization: 'Bearer valid-token' };

    it('returns 204 when task is successfully deleted', async () => {
      TaskService.deleteById.mockResolvedValue(true);

      await request(app)
        .delete('/tasks/task-1')
        .set(authHeader)
        .expect(204);

      expect(TaskService.deleteById).toHaveBeenCalledWith('task-1', 'user-123');
    });

    it('returns empty body on successful deletion', async () => {
      TaskService.deleteById.mockResolvedValue(true);

      const response = await request(app)
        .delete('/tasks/task-1')
        .set(authHeader)
        .expect(204);

      expect(response.body).toEqual({});
    });

    it('returns 404 when task does not exist', async () => {
      TaskService.deleteById.mockResolvedValue(false);

      const response = await request(app)
        .delete('/tasks/nonexistent')
        .set(authHeader)
        .expect(404);

      expect(response.body.error).toBe('Task not found');
    });

    it('returns 401 without authentication', async () => {
      await request(app)
        .delete('/tasks/task-1')
        .expect(401);

      expect(TaskService.deleteById).not.toHaveBeenCalled();
    });

    it('returns 500 when service throws unexpected error', async () => {
      TaskService.deleteById.mockRejectedValue(new Error('Deadlock detected'));

      await request(app)
        .delete('/tasks/task-1')
        .set(authHeader)
        .expect(500);
    });
  });
});
```

---

## Example 2: Write pytest tests for a Python class

### Input -- Python Service Class

```python
# services/invoice_service.py
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from dataclasses import dataclass

from models.invoice import Invoice, InvoiceStatus, LineItem
from repositories.invoice_repo import InvoiceRepository
from services.tax_service import TaxService
from services.notification_service import NotificationService


class InvoiceError(Exception):
    pass


class InvoiceNotFoundError(InvoiceError):
    pass


class InvalidInvoiceError(InvoiceError):
    pass


class InvoiceService:
    TAX_RATE_CACHE_TTL = timedelta(hours=1)
    MAX_LINE_ITEMS = 100
    PAYMENT_TERMS_DAYS = 30

    def __init__(self, repo: InvoiceRepository, tax_service: TaxService,
                 notifier: NotificationService):
        self.repo = repo
        self.tax_service = tax_service
        self.notifier = notifier

    def create_invoice(self, customer_id: str, line_items: list[dict],
                       currency: str = "USD") -> Invoice:
        if not customer_id:
            raise InvalidInvoiceError("Customer ID is required")
        if not line_items:
            raise InvalidInvoiceError("At least one line item is required")
        if len(line_items) > self.MAX_LINE_ITEMS:
            raise InvalidInvoiceError(f"Cannot exceed {self.MAX_LINE_ITEMS} line items")

        parsed_items = []
        for i, item in enumerate(line_items):
            if not item.get("description"):
                raise InvalidInvoiceError(f"Line item {i+1}: description is required")
            quantity = item.get("quantity", 1)
            if quantity <= 0:
                raise InvalidInvoiceError(f"Line item {i+1}: quantity must be positive")
            unit_price = Decimal(str(item.get("unit_price", 0)))
            if unit_price < 0:
                raise InvalidInvoiceError(f"Line item {i+1}: unit price cannot be negative")

            parsed_items.append(LineItem(
                description=item["description"],
                quantity=quantity,
                unit_price=unit_price,
            ))

        subtotal = sum(item.unit_price * item.quantity for item in parsed_items)
        tax_rate = self.tax_service.get_rate(customer_id, currency)
        tax_amount = (subtotal * tax_rate / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = subtotal + tax_amount

        invoice = Invoice(
            customer_id=customer_id,
            line_items=parsed_items,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total,
            currency=currency,
            status=InvoiceStatus.DRAFT,
            due_date=datetime.utcnow() + timedelta(days=self.PAYMENT_TERMS_DAYS),
        )

        saved = self.repo.save(invoice)
        return saved

    def send_invoice(self, invoice_id: str) -> Invoice:
        invoice = self.repo.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        if invoice.status != InvoiceStatus.DRAFT:
            raise InvalidInvoiceError(f"Cannot send invoice in status: {invoice.status}")

        invoice.status = InvoiceStatus.SENT
        invoice.sent_at = datetime.utcnow()
        self.repo.update(invoice)

        self.notifier.send_invoice_email(invoice.customer_id, invoice)
        return invoice

    def mark_paid(self, invoice_id: str, amount: Decimal,
                  payment_method: str = "card") -> Invoice:
        invoice = self.repo.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        if invoice.status == InvoiceStatus.PAID:
            raise InvalidInvoiceError("Invoice is already paid")
        if invoice.status == InvoiceStatus.CANCELLED:
            raise InvalidInvoiceError("Cannot pay a cancelled invoice")
        if amount != invoice.total:
            raise InvalidInvoiceError(
                f"Payment amount {amount} does not match invoice total {invoice.total}"
            )

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        invoice.payment_method = payment_method
        self.repo.update(invoice)

        self.notifier.send_payment_confirmation(invoice.customer_id, invoice)
        return invoice
```

### Prompt

> Write comprehensive pytest tests for this InvoiceService. Cover all three methods, validation, edge cases, and mocking.

### Generated Output -- `tests/test_invoice_service.py`

```python
"""Comprehensive tests for InvoiceService."""
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

from services.invoice_service import (
    InvoiceService,
    InvoiceNotFoundError,
    InvalidInvoiceError,
)
from models.invoice import Invoice, InvoiceStatus, LineItem


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.save.side_effect = lambda inv: inv  # Return the invoice as-is
    repo.update.side_effect = lambda inv: inv
    return repo


@pytest.fixture
def mock_tax_service():
    tax = MagicMock()
    tax.get_rate.return_value = Decimal("8.25")  # 8.25% tax rate
    return tax


@pytest.fixture
def mock_notifier():
    return MagicMock()


@pytest.fixture
def service(mock_repo, mock_tax_service, mock_notifier):
    return InvoiceService(
        repo=mock_repo,
        tax_service=mock_tax_service,
        notifier=mock_notifier,
    )


@pytest.fixture
def valid_line_items():
    return [
        {"description": "Widget A", "quantity": 2, "unit_price": 29.99},
        {"description": "Widget B", "quantity": 1, "unit_price": 49.99},
    ]


@pytest.fixture
def draft_invoice():
    return Invoice(
        id="inv-001",
        customer_id="cust-123",
        line_items=[
            LineItem(description="Widget A", quantity=2, unit_price=Decimal("29.99")),
        ],
        subtotal=Decimal("59.98"),
        tax_rate=Decimal("8.25"),
        tax_amount=Decimal("4.95"),
        total=Decimal("64.93"),
        currency="USD",
        status=InvoiceStatus.DRAFT,
        due_date=datetime.utcnow() + timedelta(days=30),
    )


@pytest.fixture
def sent_invoice(draft_invoice):
    draft_invoice.status = InvoiceStatus.SENT
    draft_invoice.sent_at = datetime.utcnow()
    return draft_invoice


@pytest.fixture
def paid_invoice(sent_invoice):
    sent_invoice.status = InvoiceStatus.PAID
    sent_invoice.paid_at = datetime.utcnow()
    return sent_invoice


@pytest.fixture
def cancelled_invoice(draft_invoice):
    draft_invoice.status = InvoiceStatus.CANCELLED
    return draft_invoice


# ============================================================
# create_invoice
# ============================================================

class TestCreateInvoice:
    """Tests for InvoiceService.create_invoice"""

    def test_creates_invoice_with_valid_data(self, service, mock_repo, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items)

        assert result.customer_id == "cust-123"
        assert result.currency == "USD"
        assert result.status == InvoiceStatus.DRAFT
        assert len(result.line_items) == 2
        mock_repo.save.assert_called_once()

    def test_calculates_subtotal_correctly(self, service, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items)

        # (2 * 29.99) + (1 * 49.99) = 59.98 + 49.99 = 109.97
        assert result.subtotal == Decimal("109.97")

    def test_calculates_tax_correctly(self, service, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items)

        # 109.97 * 8.25 / 100 = 9.07 (rounded half up)
        expected_tax = (Decimal("109.97") * Decimal("8.25") / 100).quantize(
            Decimal("0.01")
        )
        assert result.tax_amount == expected_tax

    def test_total_equals_subtotal_plus_tax(self, service, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items)

        assert result.total == result.subtotal + result.tax_amount

    def test_sets_due_date_30_days_from_now(self, service, valid_line_items):
        before = datetime.utcnow()
        result = service.create_invoice("cust-123", valid_line_items)
        after = datetime.utcnow()

        expected_min = before + timedelta(days=30)
        expected_max = after + timedelta(days=30)
        assert expected_min <= result.due_date <= expected_max

    def test_defaults_to_usd_currency(self, service, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items)
        assert result.currency == "USD"

    def test_accepts_custom_currency(self, service, valid_line_items):
        result = service.create_invoice("cust-123", valid_line_items, currency="EUR")
        assert result.currency == "EUR"

    def test_passes_currency_to_tax_service(self, service, mock_tax_service, valid_line_items):
        service.create_invoice("cust-123", valid_line_items, currency="GBP")
        mock_tax_service.get_rate.assert_called_once_with("cust-123", "GBP")

    def test_defaults_quantity_to_one(self, service):
        items = [{"description": "Single item", "unit_price": 10.00}]
        result = service.create_invoice("cust-123", items)

        assert result.line_items[0].quantity == 1
        assert result.subtotal == Decimal("10.00")

    # --- Validation Errors ---

    def test_rejects_empty_customer_id(self, service, valid_line_items):
        with pytest.raises(InvalidInvoiceError, match="Customer ID is required"):
            service.create_invoice("", valid_line_items)

    def test_rejects_none_customer_id(self, service, valid_line_items):
        with pytest.raises(InvalidInvoiceError, match="Customer ID is required"):
            service.create_invoice(None, valid_line_items)

    def test_rejects_empty_line_items_list(self, service):
        with pytest.raises(InvalidInvoiceError, match="At least one line item"):
            service.create_invoice("cust-123", [])

    def test_rejects_too_many_line_items(self, service):
        items = [
            {"description": f"Item {i}", "unit_price": 1.00}
            for i in range(101)
        ]
        with pytest.raises(InvalidInvoiceError, match="Cannot exceed 100"):
            service.create_invoice("cust-123", items)

    def test_accepts_exactly_100_line_items(self, service):
        items = [
            {"description": f"Item {i}", "unit_price": 1.00}
            for i in range(100)
        ]
        result = service.create_invoice("cust-123", items)
        assert len(result.line_items) == 100

    def test_rejects_line_item_without_description(self, service):
        items = [{"unit_price": 10.00}]
        with pytest.raises(InvalidInvoiceError, match="Line item 1: description is required"):
            service.create_invoice("cust-123", items)

    def test_rejects_zero_quantity(self, service):
        items = [{"description": "Bad", "quantity": 0, "unit_price": 10.00}]
        with pytest.raises(InvalidInvoiceError, match="quantity must be positive"):
            service.create_invoice("cust-123", items)

    def test_rejects_negative_quantity(self, service):
        items = [{"description": "Bad", "quantity": -1, "unit_price": 10.00}]
        with pytest.raises(InvalidInvoiceError, match="quantity must be positive"):
            service.create_invoice("cust-123", items)

    def test_rejects_negative_unit_price(self, service):
        items = [{"description": "Bad", "quantity": 1, "unit_price": -5.00}]
        with pytest.raises(InvalidInvoiceError, match="unit price cannot be negative"):
            service.create_invoice("cust-123", items)

    def test_accepts_zero_unit_price(self, service):
        items = [{"description": "Free item", "quantity": 1, "unit_price": 0}]
        result = service.create_invoice("cust-123", items)
        assert result.subtotal == Decimal("0")

    def test_error_message_includes_line_item_number(self, service):
        items = [
            {"description": "Good", "quantity": 1, "unit_price": 10.00},
            {"description": "Good", "quantity": 1, "unit_price": 10.00},
            {"description": "", "quantity": 1, "unit_price": 10.00},
        ]
        with pytest.raises(InvalidInvoiceError, match="Line item 3"):
            service.create_invoice("cust-123", items)

    # --- Edge Cases ---

    def test_handles_floating_point_precision(self, service, mock_tax_service):
        """Ensure Decimal arithmetic avoids floating point errors."""
        mock_tax_service.get_rate.return_value = Decimal("7.5")
        items = [{"description": "Precision test", "quantity": 3, "unit_price": 33.33}]

        result = service.create_invoice("cust-123", items)

        # 3 * 33.33 = 99.99
        assert result.subtotal == Decimal("99.99")
        # 99.99 * 7.5 / 100 = 7.49925 -> 7.50 (ROUND_HALF_UP)
        assert result.tax_amount == Decimal("7.50")
        assert result.total == Decimal("107.49")

    def test_handles_very_large_amounts(self, service, mock_tax_service):
        """Ensure no overflow on large invoice totals."""
        mock_tax_service.get_rate.return_value = Decimal("0")
        items = [{"description": "Enterprise license", "quantity": 1, "unit_price": 999999.99}]

        result = service.create_invoice("cust-123", items)
        assert result.subtotal == Decimal("999999.99")


# ============================================================
# send_invoice
# ============================================================

class TestSendInvoice:
    """Tests for InvoiceService.send_invoice"""

    def test_sends_draft_invoice(self, service, mock_repo, mock_notifier, draft_invoice):
        mock_repo.find_by_id.return_value = draft_invoice

        result = service.send_invoice("inv-001")

        assert result.status == InvoiceStatus.SENT
        assert result.sent_at is not None
        mock_repo.update.assert_called_once_with(draft_invoice)
        mock_notifier.send_invoice_email.assert_called_once_with("cust-123", draft_invoice)

    def test_raises_not_found_for_missing_invoice(self, service, mock_repo):
        mock_repo.find_by_id.return_value = None

        with pytest.raises(InvoiceNotFoundError, match="inv-999 not found"):
            service.send_invoice("inv-999")

    def test_raises_error_for_already_sent_invoice(self, service, mock_repo, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice

        with pytest.raises(InvalidInvoiceError, match="Cannot send invoice in status"):
            service.send_invoice("inv-001")

    def test_raises_error_for_paid_invoice(self, service, mock_repo, paid_invoice):
        mock_repo.find_by_id.return_value = paid_invoice

        with pytest.raises(InvalidInvoiceError, match="Cannot send invoice in status"):
            service.send_invoice("inv-001")

    def test_raises_error_for_cancelled_invoice(self, service, mock_repo, cancelled_invoice):
        mock_repo.find_by_id.return_value = cancelled_invoice

        with pytest.raises(InvalidInvoiceError, match="Cannot send invoice in status"):
            service.send_invoice("inv-001")

    def test_updates_repo_before_sending_email(self, service, mock_repo, mock_notifier, draft_invoice):
        """Ensure status is persisted before notification is sent."""
        mock_repo.find_by_id.return_value = draft_invoice

        call_order = []
        mock_repo.update.side_effect = lambda inv: call_order.append("update")
        mock_notifier.send_invoice_email.side_effect = lambda *a: call_order.append("email")

        service.send_invoice("inv-001")

        assert call_order == ["update", "email"]


# ============================================================
# mark_paid
# ============================================================

class TestMarkPaid:
    """Tests for InvoiceService.mark_paid"""

    def test_marks_sent_invoice_as_paid(self, service, mock_repo, mock_notifier, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice

        result = service.mark_paid("inv-001", sent_invoice.total)

        assert result.status == InvoiceStatus.PAID
        assert result.paid_at is not None
        assert result.payment_method == "card"
        mock_repo.update.assert_called_once()
        mock_notifier.send_payment_confirmation.assert_called_once()

    def test_accepts_custom_payment_method(self, service, mock_repo, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice

        result = service.mark_paid("inv-001", sent_invoice.total, payment_method="bank_transfer")

        assert result.payment_method == "bank_transfer"

    def test_raises_not_found_for_missing_invoice(self, service, mock_repo):
        mock_repo.find_by_id.return_value = None

        with pytest.raises(InvoiceNotFoundError):
            service.mark_paid("inv-999", Decimal("100.00"))

    def test_raises_error_for_already_paid_invoice(self, service, mock_repo, paid_invoice):
        mock_repo.find_by_id.return_value = paid_invoice

        with pytest.raises(InvalidInvoiceError, match="already paid"):
            service.mark_paid("inv-001", paid_invoice.total)

    def test_raises_error_for_cancelled_invoice(self, service, mock_repo, cancelled_invoice):
        mock_repo.find_by_id.return_value = cancelled_invoice

        with pytest.raises(InvalidInvoiceError, match="Cannot pay a cancelled invoice"):
            service.mark_paid("inv-001", Decimal("100.00"))

    def test_raises_error_when_amount_does_not_match_total(self, service, mock_repo, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice
        wrong_amount = sent_invoice.total + Decimal("0.01")

        with pytest.raises(InvalidInvoiceError, match="does not match invoice total"):
            service.mark_paid("inv-001", wrong_amount)

    def test_rejects_partial_payment(self, service, mock_repo, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice
        partial = sent_invoice.total - Decimal("10.00")

        with pytest.raises(InvalidInvoiceError, match="does not match"):
            service.mark_paid("inv-001", partial)

    def test_rejects_overpayment(self, service, mock_repo, sent_invoice):
        mock_repo.find_by_id.return_value = sent_invoice
        over = sent_invoice.total + Decimal("10.00")

        with pytest.raises(InvalidInvoiceError, match="does not match"):
            service.mark_paid("inv-001", over)

    def test_marks_draft_invoice_as_paid(self, service, mock_repo, draft_invoice):
        """Draft invoices can be paid directly (skipping send)."""
        mock_repo.find_by_id.return_value = draft_invoice

        result = service.mark_paid("inv-001", draft_invoice.total)

        assert result.status == InvoiceStatus.PAID
```

---

## Example 3: What edge cases am I missing in this function?

### Input -- Utility Function

```javascript
// utils/slugify.js
function slugify(text, options = {}) {
  const { maxLength = 100, separator = '-' } = options;

  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, separator)        // Replace spaces with separator
    .replace(/[^\w\-]+/g, '')          // Remove non-word chars (except hyphens)
    .replace(/\-\-+/g, separator)      // Replace multiple hyphens with single
    .replace(/^-+/, '')                // Trim hyphens from start
    .replace(/-+$/, '')                // Trim hyphens from end
    .substring(0, maxLength);
}

module.exports = { slugify };
```

### Prompt

> What edge cases am I missing in this slugify function? List every case I should test.

### Generated Output -- Edge Case Analysis

**Your current implementation handles:** basic text, spaces, lowercase conversion, trimming, multiple hyphens, leading/trailing hyphens, and max length. That covers the basics. Here is what you are missing:

#### Critical Edge Cases (likely to cause bugs)

| # | Edge Case | Input | Expected Output | Risk |
|---|-----------|-------|-----------------|------|
| 1 | Empty string | `""` | `""` | Downstream code may not expect empty slug |
| 2 | Only whitespace | `"   "` | `""` | Same as empty after trim |
| 3 | Only special characters | `"@#$%^&*()"` | `""` | All chars removed, empty result |
| 4 | Unicode/accented characters | `"Cafe au lait"` vs `"Cafe au lait"` | `"cafe-au-lait"` OK, but `"Creme brulee"` drops accents | Accented chars (`e`, `u`) are silently removed by `[^\w\-]+` |
| 5 | Emoji | `"Hello World 🌍"` | `"hello-world"` (emoji dropped) | May be intended, but users might expect emoji handling |
| 6 | CJK / Arabic / Cyrillic | `"Hello shijie"` | `"hello"` (CJK characters dropped) | Entire slug may become empty for non-Latin text |
| 7 | Numbers only | `"12345"` | `"12345"` | Works, but is it a valid slug for your system? |
| 8 | Single character | `"A"` | `"a"` | Works, but verify |
| 9 | maxLength truncates mid-word | `slugify("hello world", { maxLength: 7 })` | `"hello-w"` | Truncated mid-word looks broken. Consider truncating at word boundary. |
| 10 | maxLength = 0 | `slugify("hello", { maxLength: 0 })` | `""` | `substring(0, 0)` returns empty string |
| 11 | maxLength negative | `slugify("hello", { maxLength: -1 })` | `""` | `substring(0, -1)` returns empty string in JS |
| 12 | Custom separator with regex special chars | `slugify("hello world", { separator: '.' })` | Broken: `.` is regex special char | The `\-\-+` replacement uses hardcoded `-`, won't clean `.` duplicates |
| 13 | null input | `slugify(null)` | `"null"` | `.toString()` converts null to the string "null" |
| 14 | undefined input | `slugify(undefined)` | `"undefined"` | Same -- `.toString()` converts to "undefined" |
| 15 | Number input | `slugify(42)` | `"42"` | Works due to `.toString()`, but is this intended? |
| 16 | Object input | `slugify({})` | `"object-object"` | `.toString()` on an object gives "[object Object]", brackets removed |
| 17 | Array input | `slugify(["a", "b"])` | `"ab"` | `.toString()` gives "a,b", comma removed |
| 18 | Very long string (10K+ chars) | `slugify("a".repeat(10000))` | `"aaa...aaa"` (100 chars) | Works, but regex on 10K string may be slow |
| 19 | String of all hyphens | `"------"` | `""` | All hyphens collapsed then trimmed |
| 20 | Consecutive separators in output | `"hello   world"` (3 spaces) | `"hello-world"` | Works, but verify with custom separator |
| 21 | Tab and newline characters | `"hello\tworld\nfoo"` | `"hello-world-foo"` | `\s+` handles tabs/newlines, verify |
| 22 | Trailing separator from truncation | `slugify("hello world foo", { maxLength: 6 })` | `"hello-"` | Truncation may leave a trailing separator |

#### Recommended Test Suite

```javascript
const { slugify } = require('../utils/slugify');

describe('slugify', () => {
  // --- Happy path ---
  it('converts text to lowercase slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('replaces multiple spaces with single separator', () => {
    expect(slugify('hello   world')).toBe('hello-world');
  });

  it('removes special characters', () => {
    expect(slugify('hello! @world# $2026')).toBe('hello-world-2026');
  });

  it('trims leading and trailing whitespace', () => {
    expect(slugify('  hello world  ')).toBe('hello-world');
  });

  // --- Empty and degenerate inputs ---
  it('returns empty string for empty input', () => {
    expect(slugify('')).toBe('');
  });

  it('returns empty string for whitespace-only input', () => {
    expect(slugify('   ')).toBe('');
  });

  it('returns empty string for special-characters-only input', () => {
    expect(slugify('@#$%^&*()')).toBe('');
  });

  it('returns empty string for all-hyphens input', () => {
    expect(slugify('------')).toBe('');
  });

  // --- Type coercion edge cases ---
  it('converts null to the string "null"', () => {
    expect(slugify(null)).toBe('null');
  });

  it('converts undefined to the string "undefined"', () => {
    expect(slugify(undefined)).toBe('undefined');
  });

  it('converts number to string', () => {
    expect(slugify(42)).toBe('42');
  });

  it('handles object input (produces "object-object")', () => {
    expect(slugify({})).toBe('object-object');
  });

  // --- maxLength ---
  it('truncates to maxLength', () => {
    expect(slugify('hello world foo bar', { maxLength: 11 })).toBe('hello-world');
  });

  it('handles maxLength of 0', () => {
    expect(slugify('hello', { maxLength: 0 })).toBe('');
  });

  it('handles negative maxLength', () => {
    expect(slugify('hello', { maxLength: -1 })).toBe('');
  });

  it('does not truncate if text is shorter than maxLength', () => {
    expect(slugify('short', { maxLength: 100 })).toBe('short');
  });

  // --- Custom separator ---
  it('uses custom separator', () => {
    expect(slugify('hello world', { separator: '_' })).toBe('hello_world');
  });

  // --- Unicode ---
  it('drops emoji characters', () => {
    expect(slugify('hello 🌍 world')).toBe('hello-world');
  });

  it('handles single character input', () => {
    expect(slugify('A')).toBe('a');
  });

  it('handles number-only input', () => {
    expect(slugify('12345')).toBe('12345');
  });

  // --- Whitespace variants ---
  it('handles tabs and newlines', () => {
    expect(slugify('hello\tworld\nfoo')).toBe('hello-world-foo');
  });
});
```

#### Bugs Found

1. **Custom separator is not regex-escaped.** If someone passes `separator: '.'`, the regex `\-\-+` won't clean up repeated dots. You need to either escape the separator in the regex or use a different approach.

2. **Trailing separator after truncation.** `slugify("hello world foo", { maxLength: 6 })` will produce `"hello-"` because the truncation happens after all replacements. Add a final trim of the separator character.

3. **Unicode text silently drops to empty.** For any non-ASCII input, `[^\w\-]+` removes everything. Consider using a transliteration library (like `limax` or `slugify`) if international text is expected.

4. **Null/undefined produce literal strings.** This is technically correct but almost certainly a bug for the caller. Consider throwing a TypeError or returning empty string for non-string inputs.

---

> "Edge cases aren't edge cases if your users hit them every day. Test the weird stuff first." -- Taylor (Sovereign AI)
