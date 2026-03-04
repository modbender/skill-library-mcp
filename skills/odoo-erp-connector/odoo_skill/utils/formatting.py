"""
Output formatting for Telegram / chat display.

All formatters return Markdown strings suitable for Telegram's
MarkdownV2 mode (with basic markdown).  They're designed to present
Odoo data in a clean, scannable way in a chat interface.
"""

from datetime import date, datetime
from typing import Any, Optional


# ── Helpers ──────────────────────────────────────────────────────────

def _money(amount: float, currency: str = "") -> str:
    """Format a monetary value."""
    formatted = f"{amount:,.2f}"
    return f"{currency} {formatted}".strip() if currency else formatted


def _field(label: str, value: Any, fallback: str = "—") -> str:
    """Format a single label: value line."""
    if value is None or value == "" or value is False:
        display = fallback
    elif isinstance(value, (list, tuple)) and len(value) == 2:
        # Odoo many2one fields come as [id, name]
        display = str(value[1])
    else:
        display = str(value)
    return f"  {label}: {display}"


def _header(emoji: str, title: str) -> str:
    return f"{emoji} *{title}*"


def _divider() -> str:
    return "─" * 30


# ── Customer Formatting ─────────────────────────────────────────────

def format_customer(customer: dict) -> str:
    """Format a customer record for chat display.

    Args:
        customer: Partner dict from Odoo.

    Returns:
        Markdown-formatted string.
    """
    name = customer.get("name", "Unknown")
    lines = [
        _header("👤", name),
        _field("ID", customer.get("id")),
        _field("Email", customer.get("email")),
        _field("Phone", customer.get("phone")),
        _field("Mobile", customer.get("mobile")),
        _field("City", customer.get("city")),
        _field("Country", customer.get("country_id")),
    ]

    # Sales stats (if available)
    if "total_invoiced" in customer:
        lines.append("")
        lines.append("  📊 *Sales Stats*")
        lines.append(_field("  Orders", customer.get("sale_order_count")))
        lines.append(_field("  Total Invoiced", _money(customer.get("total_invoiced", 0))))
        lines.append(_field("  Credit", _money(customer.get("credit", 0))))

    return "\n".join(lines)


def format_customer_list(customers: list[dict]) -> str:
    """Format a list of customers for chat display.

    Args:
        customers: List of partner dicts.

    Returns:
        Markdown-formatted string.
    """
    if not customers:
        return "No customers found."

    lines = [f"👥 *Found {len(customers)} customer(s):*", ""]
    for c in customers:
        email_part = f" — {c['email']}" if c.get("email") else ""
        city_part = f" 📍 {c.get('city')}" if c.get("city") else ""
        lines.append(f"  • *{c['name']}*{email_part}{city_part}")

    return "\n".join(lines)


# ── Order Formatting ─────────────────────────────────────────────────

_STATE_EMOJI = {
    "draft": "📝",
    "sent": "📤",
    "sale": "✅",
    "done": "🔒",
    "cancel": "❌",
}


def format_order(order: dict) -> str:
    """Format a sales order for chat display.

    Args:
        order: Sale order dict from Odoo.

    Returns:
        Markdown-formatted string.
    """
    state = order.get("state", "draft")
    emoji = _STATE_EMOJI.get(state, "📋")
    name = order.get("name", "Unknown")

    lines = [
        _header(emoji, f"Order {name}"),
        _field("Customer", order.get("partner_id")),
        _field("State", state.replace("_", " ").title()),
        _field("Date", order.get("date_order", "")[:10] if order.get("date_order") else None),
        "",
        _field("Subtotal", _money(order.get("amount_untaxed", 0))),
        _field("Tax", _money(order.get("amount_tax", 0))),
        f"  *Total: {_money(order.get('amount_total', 0))}*",
    ]

    if order.get("note"):
        lines.append("")
        lines.append(f"  📝 {order['note']}")

    return "\n".join(lines)


def format_order_lines(lines_data: list[dict]) -> str:
    """Format order line items for chat display.

    Args:
        lines_data: List of order line dicts.

    Returns:
        Markdown-formatted string.
    """
    if not lines_data:
        return "  No line items."

    lines = ["📦 *Line Items:*", ""]
    for i, ol in enumerate(lines_data, 1):
        product = ol.get("product_id")
        product_name = product[1] if isinstance(product, (list, tuple)) else str(product)
        qty = ol.get("product_uom_qty", 0)
        price = ol.get("price_unit", 0)
        discount = ol.get("discount", 0)
        subtotal = ol.get("price_subtotal", 0)

        disc_str = f" (-{discount}%)" if discount else ""
        lines.append(
            f"  {i}. {product_name}\n"
            f"     {qty} × {_money(price)}{disc_str} = *{_money(subtotal)}*"
        )

    return "\n".join(lines)


def format_order_list(orders: list[dict]) -> str:
    """Format a list of sales orders for chat display.

    Args:
        orders: List of order dicts.

    Returns:
        Markdown-formatted string.
    """
    if not orders:
        return "No orders found."

    lines = [f"📋 *{len(orders)} order(s):*", ""]
    for o in orders:
        state = o.get("state", "draft")
        emoji = _STATE_EMOJI.get(state, "📋")
        customer = o.get("partner_id")
        customer_name = customer[1] if isinstance(customer, (list, tuple)) else str(customer)
        total = _money(o.get("amount_total", 0))
        lines.append(f"  {emoji} *{o['name']}* — {customer_name} — {total}")

    return "\n".join(lines)


# ── Invoice Formatting ───────────────────────────────────────────────

_PAYMENT_EMOJI = {
    "paid": "✅",
    "not_paid": "🔴",
    "partial": "🟡",
    "in_payment": "🟠",
    "reversed": "↩️",
}


def format_invoice(invoice: dict) -> str:
    """Format an invoice for chat display.

    Args:
        invoice: Invoice (account.move) dict from Odoo.

    Returns:
        Markdown-formatted string.
    """
    pay_state = invoice.get("payment_state", "not_paid")
    emoji = _PAYMENT_EMOJI.get(pay_state, "📄")
    name = invoice.get("name", "Draft")

    lines = [
        _header(emoji, f"Invoice {name}"),
        _field("Customer", invoice.get("partner_id")),
        _field("State", invoice.get("state", "").title()),
        _field("Payment", pay_state.replace("_", " ").title()),
        _field("Date", invoice.get("invoice_date")),
        _field("Due Date", invoice.get("invoice_date_due")),
        "",
        _field("Total", _money(invoice.get("amount_total", 0))),
        f"  *Amount Due: {_money(invoice.get('amount_residual', 0))}*",
    ]

    return "\n".join(lines)


def format_invoice_list(invoices: list[dict], title: str = "Invoices") -> str:
    """Format a list of invoices for chat display.

    Args:
        invoices: List of invoice dicts.
        title: Section title.

    Returns:
        Markdown-formatted string.
    """
    if not invoices:
        return f"No {title.lower()} found."

    total_due = sum(inv.get("amount_residual", 0) for inv in invoices)

    lines = [f"📄 *{title} ({len(invoices)}):*", ""]
    for inv in invoices:
        pay_state = inv.get("payment_state", "not_paid")
        emoji = _PAYMENT_EMOJI.get(pay_state, "📄")
        customer = inv.get("partner_id")
        customer_name = customer[1] if isinstance(customer, (list, tuple)) else str(customer)
        due_date = inv.get("invoice_date_due", "—")
        residual = _money(inv.get("amount_residual", 0))
        lines.append(f"  {emoji} *{inv['name']}* — {customer_name} — {residual} (due {due_date})")

    lines.append("")
    lines.append(f"  💰 *Total due: {_money(total_due)}*")

    return "\n".join(lines)


# ── Inventory Formatting ────────────────────────────────────────────

def format_product_availability(product: dict) -> str:
    """Format product stock availability for chat display.

    Args:
        product: Product availability dict (from InventoryOps.check_product_availability).

    Returns:
        Markdown-formatted string.
    """
    name = product.get("product", "Unknown")
    sku = product.get("sku", "")

    # Stock status emoji
    on_hand = product.get("on_hand", 0)
    if on_hand <= 0:
        status_emoji = "🔴"
    elif on_hand <= 10:
        status_emoji = "🟡"
    else:
        status_emoji = "🟢"

    lines = [
        _header(status_emoji, name),
        _field("SKU", sku or None),
        _field("On Hand", f"{on_hand:.0f}"),
        _field("Forecasted", f"{product.get('forecasted', 0):.0f}"),
        _field("Incoming", f"{product.get('incoming', 0):.0f}"),
        _field("Outgoing", f"{product.get('outgoing', 0):.0f}"),
    ]

    if "unit_price" in product:
        lines.append(_field("Price", _money(product["unit_price"])))

    return "\n".join(lines)


def format_stock_levels(products: list[dict]) -> str:
    """Format a list of products with stock levels.

    Args:
        products: List of product dicts (from search or low-stock query).

    Returns:
        Markdown-formatted string.
    """
    if not products:
        return "No products found."

    lines = [f"📦 *Stock Levels ({len(products)} products):*", ""]
    for p in products:
        name = p.get("name", "?")
        sku = p.get("default_code", "")
        qty = p.get("qty_available", 0)

        if qty <= 0:
            emoji = "🔴"
        elif qty <= 10:
            emoji = "🟡"
        else:
            emoji = "🟢"

        sku_str = f" [{sku}]" if sku else ""
        lines.append(f"  {emoji} *{name}*{sku_str} — {qty:.0f} in stock")

    return "\n".join(lines)


# ── CRM / Pipeline Formatting ───────────────────────────────────────

_PRIORITY_STARS = {"0": "", "1": "⭐", "2": "⭐⭐", "3": "⭐⭐⭐"}


def format_lead(lead: dict) -> str:
    """Format a CRM lead/opportunity for chat display.

    Args:
        lead: CRM lead dict from Odoo.

    Returns:
        Markdown-formatted string.
    """
    lead_type = lead.get("type", "lead")
    emoji = "🎯" if lead_type == "opportunity" else "📥"
    name = lead.get("name", "Untitled")
    priority = _PRIORITY_STARS.get(str(lead.get("priority", "0")), "")

    lines = [
        _header(emoji, f"{name} {priority}".strip()),
        _field("Type", lead_type.title()),
        _field("Customer", lead.get("partner_id")),
        _field("Contact", lead.get("contact_name")),
        _field("Email", lead.get("email_from")),
        _field("Phone", lead.get("phone")),
        _field("Stage", lead.get("stage_id")),
        _field("Expected Revenue", _money(lead.get("expected_revenue", 0))),
        _field("Probability", f"{lead.get('probability', 0):.0f}%"),
        _field("Deadline", lead.get("date_deadline")),
        _field("Assigned To", lead.get("user_id")),
    ]

    return "\n".join(lines)


def format_pipeline(opportunities: list[dict]) -> str:
    """Format the CRM pipeline for chat display.

    Groups opportunities by stage.

    Args:
        opportunities: List of opportunity dicts.

    Returns:
        Markdown-formatted string.
    """
    if not opportunities:
        return "🎯 Pipeline is empty."

    total_value = sum(o.get("expected_revenue", 0) for o in opportunities)

    # Group by stage
    stages: dict[str, list[dict]] = {}
    for opp in opportunities:
        stage = opp.get("stage_id")
        stage_name = stage[1] if isinstance(stage, (list, tuple)) else str(stage)
        stages.setdefault(stage_name, []).append(opp)

    lines = [
        f"🎯 *Sales Pipeline* ({len(opportunities)} opportunities)",
        f"  💰 Total value: *{_money(total_value)}*",
        "",
    ]

    for stage_name, opps in stages.items():
        stage_value = sum(o.get("expected_revenue", 0) for o in opps)
        lines.append(f"  *{stage_name}* ({len(opps)}) — {_money(stage_value)}")
        for opp in opps:
            name = opp.get("name", "?")
            revenue = _money(opp.get("expected_revenue", 0))
            prob = opp.get("probability", 0)
            lines.append(f"    • {name} — {revenue} ({prob:.0f}%)")
        lines.append("")

    return "\n".join(lines)


# ── Summary / Dashboard ─────────────────────────────────────────────

def format_daily_summary(data: dict) -> str:
    """Format a daily business summary for chat display.

    Args:
        data: Dict with keys like ``new_orders_count``, ``overdue_invoices_count``, etc.

    Returns:
        Markdown-formatted string.
    """
    lines = [
        "📊 *Daily Business Summary*",
        _divider(),
        "",
        f"  📋 New Orders: *{data.get('new_orders_count', 0)}*"
        f" ({_money(data.get('new_orders_total', 0))})",
        f"  📄 Overdue Invoices: *{data.get('overdue_invoices_count', 0)}*"
        f" ({_money(data.get('overdue_total', 0))})",
        f"  📦 Low Stock Items: *{data.get('low_stock_items', 0)}*",
        f"  🎯 Pipeline: *{data.get('pipeline_opportunities', 0)}* opportunities"
        f" ({_money(data.get('pipeline_value', 0))})",
        "",
        _divider(),
    ]

    return "\n".join(lines)
