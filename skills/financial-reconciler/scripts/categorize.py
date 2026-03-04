#!/usr/bin/env python3
"""Rule-based transaction categorization engine."""

import argparse
import json
import re
import sys

from db import ensure_db_ready, get_connection, get_categorization_rules, get_category_id


def categorize_transaction(description, rules_by_type):
    """
    Categorize a transaction description using rules in priority order:
    1. Custom rules (confidence 1.0)
    2. Exact keyword match (confidence 0.95)
    3. Partial keyword match (confidence 0.85)
    4. Regex pattern match (confidence 0.75)
    5. Uncategorized (confidence 0.0)
    """
    desc_lower = description.lower().strip()

    # 1. Custom rules (highest priority)
    for rule in rules_by_type.get("custom", []):
        if rule["pattern"].lower() == desc_lower:
            return rule["category_name"], 1.0

    # 2. Exact keyword match
    for rule in rules_by_type.get("keyword", []):
        pattern = rule["pattern"].lower()
        if pattern == desc_lower:
            return rule["category_name"], 0.95

    # 3. Partial keyword match (keyword found within description)
    best_keyword_match = None
    best_keyword_len = 0
    for rule in rules_by_type.get("keyword", []):
        pattern = rule["pattern"].lower()
        if pattern in desc_lower and len(pattern) > best_keyword_len:
            best_keyword_match = rule["category_name"]
            best_keyword_len = len(pattern)

    if best_keyword_match and best_keyword_len >= 3:
        return best_keyword_match, 0.85

    # 4. Regex pattern match
    for rule in rules_by_type.get("regex", []):
        try:
            if re.search(rule["pattern"], description, re.IGNORECASE):
                return rule["category_name"], 0.75
        except re.error:
            continue

    # 5. Uncategorized
    return "uncategorized", 0.0


def run_categorization(recategorize=False, db_path=None):
    """Run categorization on all uncategorized (or all if recategorize) transactions."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    # Load rules grouped by type
    rules = get_categorization_rules(conn)
    rules_by_type = {}
    for rule in rules:
        rule_type = rule["rule_type"]
        if rule_type not in rules_by_type:
            rules_by_type[rule_type] = []
        rules_by_type[rule_type].append(dict(rule))

    # Get transactions to categorize
    if recategorize:
        transactions = conn.execute(
            "SELECT id, description, original_description FROM transactions"
        ).fetchall()
    else:
        transactions = conn.execute(
            "SELECT id, description, original_description FROM transactions WHERE category_id IS NULL"
        ).fetchall()

    if not transactions:
        result = {
            "success": True,
            "categorized": 0,
            "already_categorized": 0,
            "message": "No transactions to categorize",
        }
        conn.close()
        return result

    # Build category name -> id mapping
    categories = conn.execute("SELECT id, name FROM categories").fetchall()
    cat_name_to_id = {row["name"]: row["id"] for row in categories}

    categorized = 0
    by_category = {}

    for tx in transactions:
        # Try matching on cleaned description first, then original
        desc = tx["description"] or tx["original_description"] or ""
        orig = tx["original_description"] or desc

        category_name, confidence = categorize_transaction(desc, rules_by_type)

        # If still uncategorized, try original description
        if category_name == "uncategorized" and orig != desc:
            category_name2, confidence2 = categorize_transaction(orig, rules_by_type)
            if category_name2 != "uncategorized":
                category_name = category_name2
                confidence = confidence2

        cat_id = cat_name_to_id.get(category_name)
        if cat_id is None:
            # Ensure uncategorized exists
            cat_id = cat_name_to_id.get("uncategorized")

        conn.execute(
            "UPDATE transactions SET category_id = ?, category_confidence = ? WHERE id = ?",
            (cat_id, confidence, tx["id"]),
        )
        categorized += 1
        by_category[category_name] = by_category.get(category_name, 0) + 1

    conn.commit()

    uncategorized_count = by_category.get("uncategorized", 0)

    result = {
        "success": True,
        "categorized": categorized,
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "uncategorized_count": uncategorized_count,
        "recategorize": recategorize,
    }

    conn.close()
    return result


def add_custom_rule(category_name, pattern, rule_type="keyword", db_path=None):
    """Add a custom categorization rule."""
    ensure_db_ready(db_path)
    conn = get_connection(db_path)

    cat_id = get_category_id(conn, category_name)
    if cat_id is None:
        conn.close()
        return {"success": False, "error": f"Category not found: {category_name}"}

    if rule_type not in ("exact", "keyword", "regex", "custom"):
        conn.close()
        return {"success": False, "error": f"Invalid rule type: {rule_type}"}

    # Custom rules get highest priority
    priority = 100 if rule_type == "custom" else 50

    conn.execute(
        "INSERT INTO categorization_rules (category_id, rule_type, pattern, priority) VALUES (?, ?, ?, ?)",
        (cat_id, rule_type, pattern, priority),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Added {rule_type} rule '{pattern}' for category '{category_name}'",
    }


def main():
    parser = argparse.ArgumentParser(description="Categorize bank transactions")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Run categorization
    run_parser = subparsers.add_parser("run", help="Run categorization")
    run_parser.add_argument("--recategorize", action="store_true",
                            help="Re-categorize all transactions, not just uncategorized")
    run_parser.add_argument("--db", help="Database path override")

    # Add rule
    add_parser = subparsers.add_parser("add-rule", help="Add a categorization rule")
    add_parser.add_argument("category", help="Category name")
    add_parser.add_argument("pattern", help="Pattern to match")
    add_parser.add_argument("--type", choices=["exact", "keyword", "regex", "custom"],
                            default="keyword", help="Rule type")
    add_parser.add_argument("--db", help="Database path override")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        recategorize = getattr(args, "recategorize", False)
        db = getattr(args, "db", None)
        result = run_categorization(recategorize=recategorize, db_path=db)
    elif args.command == "add-rule":
        result = add_custom_rule(args.category, args.pattern,
                                 rule_type=args.type, db_path=args.db)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
