---
name: Business Claw Skills
description: High-level business workflows that combine multiple MCP tools into
  reusable, executable skills for ERPNext.
---

# Business Claw Skills

High-level business workflows that combine multiple MCP tools into reusable, executable skills for ERPNext.

## Overview

Skills are pre-defined workflows stored as JSON files in [`definitions/`](definitions/). Each skill defines:
- **Triggers**: Natural language patterns that activate the skill
- **Tools**: MCP tools to execute in sequence
- **Input Schema**: Required and optional parameters
- **Workflow Steps**: Ordered execution plan with variable substitution
- **Guardrails**: Validation rules for safe execution
- **Output Template**: Formatted response message

## Available Skills

### CRM Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`create_customer`](definitions/create_customer.json) | Create a new customer with contact and address | crm |
| [`create_lead`](definitions/create_lead.json) | Register a new lead | crm |
| [`create_supplier`](definitions/create_supplier.json) | Add a new supplier | crm |

### Sales Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`create_sales_order`](definitions/create_sales_order.json) | Create a sales order | sales |
| [`create_quotation`](definitions/create_quotation.json) | Create a quotation | sales |
| [`create_invoice`](definitions/create_invoice.json) | Generate sales invoice | sales |
| [`complete_sales_workflow`](definitions/complete_sales_workflow.json) | Full Quotation → SO → Invoice → Payment | sales |

### Purchase Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`create_purchase_order`](definitions/create_purchase_order.json) | Create a purchase order | purchase |

### Inventory Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`create_item`](definitions/create_item.json) | Create new item in inventory | inventory |
| [`stock_entry`](definitions/stock_entry.json) | Record stock movements | inventory |

### Project Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`create_project`](definitions/create_project.json) | Create a new project | project |

### Financial Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`process_payment`](definitions/process_payment.json) | Record payment entry | payments |

### Utility Skills

| Skill | Description | Category |
|-------|-------------|----------|
| [`search_records`](definitions/search_records.json) | Search across DocTypes | utility |
| [`bulk_operation`](definitions/bulk_operation.json) | Bulk create/update/delete | utility |
| [`generic_task`](definitions/generic_task.json) | Flexible multi-step workflow | utility |

## Usage

### Loading Skills

```python
from bc_skills import get_available_skills, load_skill

# List all available skills
skills = get_available_skills()
print(skills)  # ['create_customer', 'create_sales_order', ...]

# Load a specific skill
skill = load_skill("create_customer")
```

### Executing Skills

```python
from bc_skills.loader import execute_skill

result = execute_skill(
    name="create_customer",
    context={
        "customer_name": "ACME Corp",
        "customer_type": "Company",
        "customer_group": "Commercial",
        "email": "contact@acme.com"
    },
    user="Administrator"
)

print(result)
```

### Trigger Examples

Skills respond to natural language triggers:

| Trigger Phrase | Skill |
|----------------|-------|
| "create customer" | create_customer |
| "add customer" | create_customer |
| "new customer" | create_customer |
| "complete sales workflow" | complete_sales_workflow |
| "full sales process" | complete_sales_workflow |
| "process order to payment" | complete_sales_workflow |
| "create sales order" | create_sales_order |
| "generate invoice" | create_invoice |

## Skill Definition Schema

```json
{
  "name": "skill_name",
  "version": "1.0.0",
  "description": "What the skill does",
  "author": "Business Claw Team",
  "category": "crm|sales|purchase|inventory|project|payments|utility",
  
  "triggers": [
    "trigger phrase 1",
    "trigger phrase 2"
  ],
  
  "tools": [
    {
      "name": "tool_name",
      "description": "What it does",
      "required": true
    }
  ],
  
  "input_schema": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string",
        "description": "Parameter description",
        "enum": ["option1", "option2"]
      }
    },
    "required": ["required_param"]
  },
  
  "workflow": {
    "steps": [
      {
        "step": "step_name",
        "tool": "tool_to_call",
        "arguments": {
          "doctype": "DocType",
          "data": {
            "field": "${variable}"
          }
        }
      }
    ]
  },
  
  "guardrails": {
    "rule_name": true
  },
  
  "output_template": "Formatted output {{variable}}"
}
```

## Variable Substitution

Workflow steps support `${variable}` substitution from execution context:

```json
{
  "step": "create_order",
  "tool": "create_document",
  "arguments": {
    "doctype": "Sales Order",
    "data": {
      "customer": "${customer_id}",
      "items": "${items}"
    }
  }
}
```

## Creating Custom Skills

1. Create a JSON file in [`definitions/`](definitions/)
2. Define triggers, tools, input schema, and workflow
3. Use the `SkillLoader` to load and execute

Example custom skill structure:

```json
{
  "name": "my_custom_skill",
  "version": "1.0.0",
  "description": "My custom workflow",
  "category": "utility",
  "triggers": ["my trigger"],
  "tools": [
    {"name": "get_doctype_meta", "required": true},
    {"name": "create_document", "required": true}
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "param1": {"type": "string"}
    },
    "required": ["param1"]
  },
  "workflow": {
    "steps": [
      {
        "step": "step1",
        "tool": "get_doctype_meta",
        "arguments": {"doctype": "Item"}
      }
    ]
  },
  "output_template": "Result: {{result}}"
}
```

## Architecture

- [`loader.py`](loader.py) - `SkillLoader` class manages skill loading and execution
- [`definitions/`](definitions/) - JSON files containing skill definitions
- Skills use the `ToolRouter` to execute MCP tools in sequence
- Guardrails provide validation before skill execution

## Requirements

- Frappe/ERPNext environment
- `bc_mcp` module for tool routing
- JSON or YAML skill definitions

## License

MIT