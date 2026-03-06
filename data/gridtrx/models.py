"""
GridTRX — Data Model & Database Layer (v2)
NV-style architecture: reports contain ordered items.
Items can be posting accounts, total accounts, labels, or separators.
6 total-to columns enable flexible report arithmetic.
All amounts stored as integers (cents). Double-entry enforced.
One data layer — CLI, MCP server, and browser UI all call these functions.
"""
import sqlite3, os
from datetime import datetime, date
from contextlib import contextmanager

DB_PATH = None
def get_db_path(): return DB_PATH
def set_db_path(path):
    global DB_PATH
    DB_PATH = path

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(path):
    set_db_path(path)
    with get_db() as db:
        db.executescript(SCHEMA)
    _ensure_columns()

def _ensure_columns():
    """Add columns that may be missing from older database files."""
    with get_db() as db:
        cols = {r[1] for r in db.execute("PRAGMA table_info(lines)").fetchall()}
        if 'doc_on_file' not in cols:
            db.execute("ALTER TABLE lines ADD COLUMN doc_on_file INTEGER DEFAULT 0")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0,
    period_begin TEXT DEFAULT '',
    period_end TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS report_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL REFERENCES reports(id),
    position INTEGER NOT NULL DEFAULT 0,
    item_type TEXT NOT NULL DEFAULT 'account'
        CHECK(item_type IN ('account','total','label','separator')),
    description TEXT DEFAULT '',
    account_id INTEGER REFERENCES accounts(id),
    indent INTEGER DEFAULT 0,
    total_to_1 TEXT DEFAULT '',
    total_to_2 TEXT DEFAULT '',
    total_to_3 TEXT DEFAULT '',
    total_to_4 TEXT DEFAULT '',
    total_to_5 TEXT DEFAULT '',
    total_to_6 TEXT DEFAULT '',
    sep_style TEXT DEFAULT '' CHECK(sep_style IN ('','single','double','blank'))
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT DEFAULT '',
    normal_balance TEXT NOT NULL CHECK(normal_balance IN ('D','C')),
    account_type TEXT DEFAULT 'posting' CHECK(account_type IN ('posting','total')),
    account_number TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    reference TEXT DEFAULT '',
    description TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    amount INTEGER NOT NULL,
    description TEXT DEFAULT '',
    reconciled INTEGER DEFAULT 0,
    doc_on_file INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_lines_txn ON lines(transaction_id);
CREATE INDEX IF NOT EXISTS idx_lines_acct ON lines(account_id);
CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date);

CREATE TABLE IF NOT EXISTS tax_codes (
    id TEXT PRIMARY KEY,
    description TEXT DEFAULT '',
    rate_percent REAL NOT NULL DEFAULT 0,
    collected_account TEXT DEFAULT '',
    paid_account TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS import_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    account_name TEXT NOT NULL,
    tax_code TEXT DEFAULT '',
    priority INTEGER DEFAULT 0,
    notes TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_rules_kw ON import_rules(keyword);
"""

# ─── Meta ──────────────────────────────────────────────────────────
def get_meta(key, default=''):
    with get_db() as db:
        row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row['value'] if row else default

def set_meta(key, value):
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)", (key, value))

# ─── Reports ──────────────────────────────────────────────────────
def get_reports():
    with get_db() as db:
        return db.execute("SELECT * FROM reports ORDER BY sort_order, id").fetchall()

def get_report(report_id):
    with get_db() as db:
        return db.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()

def add_report(name, description='', sort_order=0):
    with get_db() as db:
        cur = db.execute("INSERT INTO reports(name, description, sort_order) VALUES(?,?,?)",
            (name, description, sort_order))
        return cur.lastrowid

def update_report(report_id, description=None, sort_order=None):
    """Update a report's description and/or sort order."""
    with get_db() as db:
        rpt = db.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
        if not rpt:
            raise ValueError(f"Report ID {report_id} not found.")
        new_desc = description if description is not None else rpt['description']
        new_sort = sort_order if sort_order is not None else rpt['sort_order']
        db.execute("UPDATE reports SET description=?, sort_order=? WHERE id=?",
                   (new_desc, new_sort, report_id))
        return dict(db.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone())

# ─── Accounts ─────────────────────────────────────────────────────
def get_account(account_id):
    with get_db() as db:
        return db.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()

def get_account_by_name(name):
    with get_db() as db:
        return db.execute("SELECT * FROM accounts WHERE name=? COLLATE NOCASE", (name,)).fetchone()

def get_accounts():
    with get_db() as db:
        return db.execute("SELECT * FROM accounts ORDER BY name").fetchall()

def add_account(name, normal_balance='D', description='', account_type='posting', account_number=''):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO accounts(name, normal_balance, description, account_type, account_number) VALUES(?,?,?,?,?)",
            (name, normal_balance, description, account_type, account_number))
        return cur.lastrowid

def search_accounts(query):
    with get_db() as db:
        q = f"%{query}%"
        return db.execute("SELECT * FROM accounts WHERE name LIKE ? OR description LIKE ? ORDER BY name", (q, q)).fetchall()

# ─── Report Items ─────────────────────────────────────────────────
def get_report_items(report_id):
    with get_db() as db:
        return db.execute(
            "SELECT ri.*, a.name as acct_name, a.description as acct_desc, "
            "a.normal_balance, a.account_type, a.account_number "
            "FROM report_items ri LEFT JOIN accounts a ON ri.account_id = a.id "
            "WHERE ri.report_id=? ORDER BY ri.position", (report_id,)).fetchall()

def add_report_item(report_id, item_type='account', description='', account_id=None,
                    indent=0, position=None, total_to_1='', total_to_2='',
                    total_to_3='', total_to_4='', total_to_5='', total_to_6='',
                    sep_style=''):
    if item_type == 'total' and account_id is None:
        raise ValueError(
            f"Total report items require an account_id (the total account that accumulates). "
            f"Description: '{description}'. Create a total-type account first, then pass its id.")
    with get_db() as db:
        if position is None:
            row = db.execute("SELECT MAX(position) as mx FROM report_items WHERE report_id=?", (report_id,)).fetchone()
            position = (row['mx'] or 0) + 10
        cur = db.execute(
            "INSERT INTO report_items(report_id, position, item_type, description, account_id, "
            "indent, total_to_1, total_to_2, total_to_3, total_to_4, total_to_5, total_to_6, sep_style) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (report_id, position, item_type, description, account_id,
             indent, total_to_1, total_to_2, total_to_3, total_to_4, total_to_5, total_to_6, sep_style))
        new_id = cur.lastrowid
        # Resequence to clean up any collisions
        _resequence(db, report_id)
        return new_id

def _resequence(db, report_id):
    """Resequence all items in a report to positions 10, 20, 30, ..."""
    items = db.execute(
        "SELECT id FROM report_items WHERE report_id=? ORDER BY position, id",
        (report_id,)).fetchall()
    for i, item in enumerate(items):
        db.execute("UPDATE report_items SET position=? WHERE id=?", ((i + 1) * 10, item['id']))

def resequence_report(report_id):
    """Public wrapper for resequencing."""
    with get_db() as db:
        _resequence(db, report_id)

def move_report_item(item_id, direction):
    """Move a report item up (-1) or down (+1). Returns True if moved."""
    with get_db() as db:
        item = db.execute("SELECT id, report_id, position FROM report_items WHERE id=?", (item_id,)).fetchone()
        if not item:
            return False
        report_id = item['report_id']
        # Get all items in order
        items = db.execute(
            "SELECT id, position FROM report_items WHERE report_id=? ORDER BY position, id",
            (report_id,)).fetchall()
        # Find current index
        idx = None
        for i, it in enumerate(items):
            if it['id'] == item_id:
                idx = i
                break
        if idx is None:
            return False
        swap_idx = idx + direction
        if swap_idx < 0 or swap_idx >= len(items):
            return False
        # Swap the two items' positions
        my_pos = items[idx]['position']
        other_pos = items[swap_idx]['position']
        other_id = items[swap_idx]['id']
        # If positions are the same (collision), assign distinct values first
        if my_pos == other_pos:
            # Resequence everything, then re-find and swap
            _resequence(db, report_id)
            items = db.execute(
                "SELECT id, position FROM report_items WHERE report_id=? ORDER BY position, id",
                (report_id,)).fetchall()
            for i, it in enumerate(items):
                if it['id'] == item_id:
                    idx = i
                    break
            swap_idx = idx + direction
            if swap_idx < 0 or swap_idx >= len(items):
                return False
            my_pos = items[idx]['position']
            other_pos = items[swap_idx]['position']
            other_id = items[swap_idx]['id']
        db.execute("UPDATE report_items SET position=? WHERE id=?", (other_pos, item_id))
        db.execute("UPDATE report_items SET position=? WHERE id=?", (my_pos, other_id))
        return True

def update_report_item(item_id, **kwargs):
    """Update any fields on a report item. Pass field=value pairs."""
    allowed = {'description','indent','total_to_1','total_to_2','total_to_3',
               'total_to_4','total_to_5','total_to_6','sep_style','position','item_type'}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    with get_db() as db:
        sets = ', '.join(f'{k}=?' for k in fields)
        vals = list(fields.values()) + [item_id]
        db.execute(f"UPDATE report_items SET {sets} WHERE id=?", vals)

def delete_report_item(item_id):
    """Delete a report item. Refuses if it's a total account that other items reference."""
    with get_db() as db:
        item = db.execute("SELECT ri.*, a.name as acct_name FROM report_items ri "
            "LEFT JOIN accounts a ON ri.account_id=a.id WHERE ri.id=?", (item_id,)).fetchone()
        if not item:
            raise ValueError("Item not found")
        # If it's an account/total with a name, check if anything totals TO it
        if item['acct_name']:
            refs = db.execute("SELECT COUNT(*) as cnt FROM report_items WHERE "
                "total_to_1=? OR total_to_2=? OR total_to_3=? OR total_to_4=? OR total_to_5=? OR total_to_6=?",
                tuple([item['acct_name']] * 6)).fetchone()
            if refs['cnt'] > 0:
                raise ValueError(f"Cannot delete: {refs['cnt']} item(s) total to {item['acct_name']}")
        # If it's a posting account with transactions, refuse
        if item['account_id'] and item['item_type'] == 'account':
            acct = db.execute("SELECT account_type FROM accounts WHERE id=?", (item['account_id'],)).fetchone()
            if acct and acct['account_type'] == 'posting':
                txns = db.execute("SELECT COUNT(*) as cnt FROM lines WHERE account_id=?", (item['account_id'],)).fetchone()
                if txns['cnt'] > 0:
                    raise ValueError(f"Cannot delete: account has {txns['cnt']} transaction line(s)")
        db.execute("DELETE FROM report_items WHERE id=?", (item_id,))

def clear_report_items(report_id):
    """Delete ALL items from a report. Used by bulk_report_layout replace mode."""
    with get_db() as db:
        db.execute("DELETE FROM report_items WHERE report_id=?", (report_id,))

def update_account(account_id, description=None, account_number=None):
    """Update account description and/or account number."""
    with get_db() as db:
        if description is not None:
            db.execute("UPDATE accounts SET description=? WHERE id=?", (description, account_id))
        if account_number is not None:
            db.execute("UPDATE accounts SET account_number=? WHERE id=?", (account_number, account_id))

def find_report_for_account(account_id):
    """Find which report contains this account (returns first match)."""
    with get_db() as db:
        row = db.execute("""
            SELECT r.* FROM reports r
            JOIN report_items ri ON ri.report_id = r.id
            WHERE ri.account_id = ? AND ri.item_type = 'account'
            ORDER BY r.id LIMIT 1
        """, (account_id,)).fetchone()
        return dict(row) if row else None

def get_report_accounts(report_id):
    """Get all posting accounts belonging to a report, in position order."""
    with get_db() as db:
        return db.execute("""
            SELECT a.id, a.name, a.description, a.normal_balance
            FROM report_items ri
            JOIN accounts a ON ri.account_id = a.id
            WHERE ri.report_id = ? AND ri.item_type = 'account'
              AND a.account_type = 'posting'
            ORDER BY ri.position
        """, (report_id,)).fetchall()

def find_report_by_name(name):
    """Find a report by name (case-insensitive partial match)."""
    with get_db() as db:
        row = db.execute("SELECT * FROM reports WHERE name LIKE ? COLLATE NOCASE ORDER BY id LIMIT 1",
            (f'%{name}%',)).fetchone()
        return dict(row) if row else None

# ─── Transactions & Lines ─────────────────────────────────────────

def generate_ref():
    """Generate a random 5-char alphanumeric reference (lowercase + digits)."""
    import random, string
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(5))

def add_transaction(date_str, reference, description, lines, _bypass_ceiling=False):
    total = sum(l[1] for l in lines)
    if total != 0:
        raise ValueError(f"Transaction does not balance: off by {total/100:.2f}")
    if len(lines) < 2:
        raise ValueError("Transaction must have at least 2 lines")
    # Auto-assign reference if blank
    if not reference or not reference.strip():
        reference = generate_ref()
    # Block posting to total accounts
    with get_db() as db:
        for acct_id, amount, desc in lines:
            acct = db.execute("SELECT name, account_type FROM accounts WHERE id=?", (acct_id,)).fetchone()
            if acct and acct['account_type'] == 'total':
                raise ValueError(f"Cannot post to '{acct['name']}' — it is a total account. Post to a detail account instead.")
    # Lock date enforcement
    lock = get_meta('lock_date', '')
    if lock and date_str <= lock:
        raise ValueError(f"Date {date_str} is on or before the lock date ({lock}). Posting is not allowed.")
    # Fiscal year ceiling enforcement
    if not _bypass_ceiling:
        ceiling = get_meta('fy_end_date', '')
        if ceiling and date_str > ceiling:
            raise ValueError(
                f"Date {date_str} is after the fiscal year end ({ceiling}). "
                f"Run 'rollforward' to advance to the next fiscal year.")
    with get_db() as db:
        cur = db.execute("INSERT INTO transactions(date, reference, description) VALUES(?,?,?)",
            (date_str, reference, description))
        txn_id = cur.lastrowid
        for i, (acct_id, amount, desc) in enumerate(lines):
            db.execute("INSERT INTO lines(transaction_id, account_id, amount, description, sort_order) VALUES(?,?,?,?,?)",
                (txn_id, acct_id, amount, desc, i))
        return txn_id

def add_simple_transaction(date_str, reference, description, debit_acct_id, credit_acct_id, amount_cents):
    return add_transaction(date_str, reference, description, [
        (debit_acct_id, amount_cents, description),
        (credit_acct_id, -amount_cents, description)])

def get_transaction(txn_id):
    with get_db() as db:
        txn = db.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)).fetchone()
        if not txn: return None, []
        lines = db.execute(
            "SELECT l.*, a.name as account_name, a.normal_balance, a.description as acct_desc "
            "FROM lines l JOIN accounts a ON l.account_id=a.id WHERE l.transaction_id=? ORDER BY l.sort_order",
            (txn_id,)).fetchall()
        return txn, lines

def update_transaction(txn_id, date_str, reference, description, lines):
    """Update a transaction. lines = [(acct_id, amount, desc), ...] or
    [(acct_id, amount, desc, reconciled, doc_on_file), ...] to preserve flags."""
    total = sum(l[1] for l in lines)
    if total != 0:
        raise ValueError(f"Transaction does not balance: off by {total/100:.2f}")
    lock = get_meta('lock_date', '')
    if lock and date_str <= lock:
        raise ValueError(f"Date {date_str} is on or before the lock date ({lock}).")
    with get_db() as db:
        # Block posting to total accounts
        for line in lines:
            acct_id = line[0]
            acct = db.execute("SELECT name, account_type FROM accounts WHERE id=?",
                              (acct_id,)).fetchone()
            if acct and acct['account_type'] == 'total':
                raise ValueError(
                    f"Cannot post to '{acct['name']}' — it is a total account. "
                    "Post to a detail account instead.")
        db.execute("UPDATE transactions SET date=?, reference=?, description=? WHERE id=?",
            (date_str, reference, description, txn_id))
        db.execute("DELETE FROM lines WHERE transaction_id=?", (txn_id,))
        for i, line in enumerate(lines):
            acct_id, amount, desc = line[0], line[1], line[2]
            reconciled = line[3] if len(line) > 3 else 0
            doc_flag = line[4] if len(line) > 4 else 0
            db.execute("INSERT INTO lines(transaction_id, account_id, amount, description, reconciled, doc_on_file, sort_order) VALUES(?,?,?,?,?,?,?)",
                (txn_id, acct_id, amount, desc, reconciled, doc_flag, i))

def delete_transaction(txn_id):
    with get_db() as db:
        lock = get_meta('lock_date', '')
        if lock:
            txn = db.execute("SELECT date FROM transactions WHERE id=?", (txn_id,)).fetchone()
            if txn and txn['date'] <= lock:
                raise ValueError(f"Cannot delete: transaction date {txn['date']} is on or before lock date ({lock}).")
        db.execute("DELETE FROM transactions WHERE id=?", (txn_id,))

def bulk_delete_transactions(txn_ids):
    """Delete multiple transactions at once. Respects lock date."""
    with get_db() as db:
        lock = get_meta('lock_date', '')
        skipped = 0
        deleted = 0
        for tid in txn_ids:
            if lock:
                txn = db.execute("SELECT date FROM transactions WHERE id=?", (tid,)).fetchone()
                if txn and txn['date'] <= lock:
                    skipped += 1
                    continue
            db.execute("DELETE FROM transactions WHERE id=?", (tid,))
            deleted += 1
        return deleted, skipped

def toggle_reconcile(line_id):
    with get_db() as db:
        row = db.execute("SELECT reconciled FROM lines WHERE id=?", (line_id,)).fetchone()
        new_val = 0 if row['reconciled'] else 1
        db.execute("UPDATE lines SET reconciled=? WHERE id=?", (new_val, line_id))
        return new_val

def toggle_doc_on_file(line_id):
    """Toggle doc_on_file for ALL lines in the same transaction."""
    with get_db() as db:
        row = db.execute("SELECT doc_on_file, transaction_id FROM lines WHERE id=?", (line_id,)).fetchone()
        new_val = 0 if row['doc_on_file'] else 1
        db.execute("UPDATE lines SET doc_on_file=? WHERE transaction_id=?", (new_val, row['transaction_id']))
        return new_val

def batch_reconcile(line_ids, value=1):
    """Set reconciled flag on multiple lines at once."""
    with get_db() as db:
        for lid in line_ids:
            db.execute("UPDATE lines SET reconciled=? WHERE id=?", (value, lid))

def get_reconcile_summary(account_id):
    """Get reconciliation totals for an account."""
    with get_db() as db:
        acct = get_account(account_id)
        sign = 1 if acct['normal_balance'] == 'D' else -1
        # Total of all lines (= book balance)
        book = db.execute(
            "SELECT COALESCE(SUM(l.amount),0) FROM lines l JOIN transactions t ON l.transaction_id=t.id WHERE l.account_id=?",
            (account_id,)).fetchone()[0] * sign
        # Total of reconciled lines
        cleared = db.execute(
            "SELECT COALESCE(SUM(l.amount),0) FROM lines l JOIN transactions t ON l.transaction_id=t.id WHERE l.account_id=? AND l.reconciled=1",
            (account_id,)).fetchone()[0] * sign
        return {'book_balance': book, 'cleared_balance': cleared, 'uncleared': book - cleared}

# ─── Ledger ───────────────────────────────────────────────────────
def get_ledger(account_id, date_from=None, date_to=None, opening_balance=0):
    with get_db() as db:
        sql = """
            WITH txn_counts AS (
                SELECT transaction_id, COUNT(*) as line_count
                FROM lines GROUP BY transaction_id
            )
            SELECT t.id as txn_id, t.date, t.reference, t.description as txn_desc,
                   l.amount, l.description as line_desc, l.id as line_id, l.reconciled,
                   l.doc_on_file,
                   GROUP_CONCAT(DISTINCT a2.name) as cross_accounts,
                   tc.line_count
            FROM lines l
            JOIN transactions t ON l.transaction_id = t.id
            JOIN txn_counts tc ON tc.transaction_id = t.id
            LEFT JOIN lines l2 ON l2.transaction_id = t.id AND l2.account_id != ?
            LEFT JOIN accounts a2 ON l2.account_id = a2.id
            WHERE l.account_id = ?"""
        params = [account_id, account_id]
        if date_from: sql += " AND t.date >= ?"; params.append(date_from)
        if date_to: sql += " AND t.date <= ?"; params.append(date_to)
        sql += " GROUP BY l.id ORDER BY t.date, t.id, l.sort_order"
        rows = db.execute(sql, params).fetchall()
        acct = get_account(account_id)
        sign = 1 if acct['normal_balance'] == 'D' else -1
        result, balance = [], opening_balance
        for row in rows:
            display_amount = row['amount'] * sign  # Flip for credit-normal accounts
            balance += display_amount
            result.append({
                'txn_id': row['txn_id'], 'line_id': row['line_id'],
                'date': row['date'], 'reference': row['reference'],
                'description': row['line_desc'] or row['txn_desc'],
                'amount': display_amount, 'raw_amount': row['amount'],
                'cross_accounts': row['cross_accounts'] or '',
                'running_balance': balance, 'reconciled': row['reconciled'],
                'doc_on_file': row['doc_on_file'],
                'line_count': row['line_count']})
        return result

# ─── Balance Computation ──────────────────────────────────────────
def get_account_balance(account_id, date_from=None, date_to=None):
    """Raw sum of lines (D positive, C negative) in date range."""
    with get_db() as db:
        sql = "SELECT COALESCE(SUM(l.amount),0) as total FROM lines l JOIN transactions t ON l.transaction_id=t.id WHERE l.account_id=?"
        params = [account_id]
        if date_from: sql += " AND t.date >= ?"; params.append(date_from)
        if date_to: sql += " AND t.date <= ?"; params.append(date_to)
        return db.execute(sql, params).fetchone()['total']

def get_all_account_balances(date_from=None, date_to=None):
    """Bulk fetch: raw balance for ALL accounts in one query. Returns {account_id: balance}."""
    with get_db() as db:
        if not date_from and not date_to:
            # No date filter — skip the JOIN to transactions (12x faster on large files)
            sql = "SELECT account_id, COALESCE(SUM(amount),0) as total FROM lines GROUP BY account_id"
            rows = db.execute(sql).fetchall()
        else:
            sql = ("SELECT l.account_id, COALESCE(SUM(l.amount),0) as total "
                   "FROM lines l JOIN transactions t ON l.transaction_id=t.id WHERE 1=1")
            params = []
            if date_from: sql += " AND t.date >= ?"; params.append(date_from)
            if date_to: sql += " AND t.date <= ?"; params.append(date_to)
            sql += " GROUP BY l.account_id"
            rows = db.execute(sql, params).fetchall()
        return {r['account_id']: r['total'] for r in rows}

def get_all_report_items():
    """Get all report items across ALL reports. Used for building the global total-to chain."""
    with get_db() as db:
        return db.execute(
            "SELECT ri.*, a.name as acct_name, a.description as acct_desc, "
            "a.normal_balance, a.account_type, a.account_number "
            "FROM report_items ri LEFT JOIN accounts a ON ri.account_id = a.id "
            "ORDER BY ri.report_id, ri.position").fetchall()

def compute_report_column(report_id, date_from=None, date_to=None,
                          _display_items=None, _all_items=None):
    """
    Compute one analysis column for a report.
    The total-to chain is GLOBAL across all reports (BS, IS, RE.OFS all cross-talk).
    Uses raw DB balances for accumulation, applies display sign at the end.
    Each account is processed ONCE (first occurrence with total-to wins) to avoid
    double-counting when the same account appears on multiple reports.
    """
    display_items = _display_items or get_report_items(report_id)
    all_items = _all_items or get_all_report_items()
    tt_fields = ['total_to_1','total_to_2','total_to_3','total_to_4','total_to_5']

    # Step 1: Get RAW balances for all posting accounts in ONE query
    bulk_bal = get_all_account_balances(date_from, date_to)
    raw_bal = {}
    seen = set()
    for it in all_items:
        if it['account_id'] and it['account_type'] == 'posting' and it['acct_name'] not in seen:
            seen.add(it['acct_name'])
            raw_bal[it['acct_name']] = bulk_bal.get(it['account_id'], 0)

    # Step 2: Deduplicate items by account name.
    # For each account name, we only process it ONCE for total-to purposes.
    # If the same account appears on multiple reports with different total-to's,
    # merge all total-to targets from all occurrences.
    # For items without an account name (labels, separators), skip.
    acct_tt = {}  # name -> set of (field, target) pairs
    acct_meta = {}  # name -> first item's metadata
    for it in all_items:
        name = it['acct_name']
        if not name:
            continue
        if name not in acct_meta:
            acct_meta[name] = it
        # Collect all total-to targets from all occurrences
        if name not in acct_tt:
            acct_tt[name] = set()
        for ttf in tt_fields:
            target = it[ttf]
            if target:
                acct_tt[name].add(target)

    # Step 3: Multi-pass accumulation until stable.
    # An account's value = its own raw balance (if posting) + anything accumulated into it.
    # This handles posting accounts that are also accumulation targets
    # (e.g., AR receives from AR.ALL sub-ledger but also has its own postings).
    accumulated = {}
    
    for _pass in range(10):
        prev = dict(accumulated)
        accumulated = {}
        
        for name, targets in acct_tt.items():
            if not targets:
                continue
            # Value = own raw balance + anything accumulated into this account
            own_raw = raw_bal.get(name, 0)
            acc_into = prev.get(name, 0)
            val = own_raw + acc_into
            
            # Dump into each unique target
            for target in targets:
                accumulated[target] = accumulated.get(target, 0) + val
        
        if accumulated == prev:
            break

    # Step 4: Merge — each account's display value is raw + accumulated
    merged = {}
    all_names = set(raw_bal.keys()) | set(accumulated.keys())
    for name in all_names:
        merged[name] = raw_bal.get(name, 0) + accumulated.get(name, 0)

    # Build normal_balance map
    nb_map = {}
    for it in all_items:
        if it['acct_name'] and it['normal_balance']:
            nb_map[it['acct_name']] = it['normal_balance']

    # Step 5: Return display items with sign-adjusted balances
    result = []
    for it in display_items:
        name = it['acct_name']
        raw = merged.get(name, 0) if name else 0
        nb = nb_map.get(name, it['normal_balance'] or 'D')
        sign = 1 if nb == 'D' else -1
        result.append((dict(it), raw * sign))
    return result


def trace_account(account_name, date_from=None, date_to=None):
    """Trace the full accumulation tree for a report account.

    Returns a dict with:
      name, normal_balance, own_raw, accumulated, merged, display,
      contributors: [{name, own_raw, accumulated, value_dumped, display, targets, report}]

    The contributors list shows every account that feeds into this one
    (directly via total_to), with the amounts from the current accumulation pass.
    """
    all_items = get_all_report_items()
    tt_fields = ['total_to_1','total_to_2','total_to_3','total_to_4','total_to_5']

    bulk_bal = get_all_account_balances(date_from, date_to)
    raw_bal = {}
    seen = set()
    for it in all_items:
        if it['account_id'] and it['account_type'] == 'posting' and it['acct_name'] not in seen:
            seen.add(it['acct_name'])
            raw_bal[it['acct_name']] = bulk_bal.get(it['account_id'], 0)

    acct_tt = {}
    for it in all_items:
        name = it['acct_name']
        if not name:
            continue
        if name not in acct_tt:
            acct_tt[name] = set()
        for ttf in tt_fields:
            target = it[ttf]
            if target:
                acct_tt[name].add(target)

    # Multi-pass accumulation (same as compute_report_column)
    accumulated = {}
    for _pass in range(10):
        prev = dict(accumulated)
        accumulated = {}
        for name, targets in acct_tt.items():
            if not targets:
                continue
            val = raw_bal.get(name, 0) + prev.get(name, 0)
            for target in targets:
                accumulated[target] = accumulated.get(target, 0) + val
        if accumulated == prev:
            break

    # Build normal_balance map and report map
    nb_map = {}
    report_map = {}
    for it in all_items:
        if it['acct_name']:
            if it['normal_balance']:
                nb_map[it['acct_name']] = it['normal_balance']
            if it['acct_name'] not in report_map:
                report_map[it['acct_name']] = it['report_id']

    target_name = account_name.upper()
    target_nb = nb_map.get(target_name, 'D')
    sign = 1 if target_nb == 'D' else -1
    own_raw = raw_bal.get(target_name, 0)
    acc_into = accumulated.get(target_name, 0)
    merged = own_raw + acc_into
    display = merged * sign

    # Find direct contributors: accounts whose total_to includes target_name
    contributors = []
    for name, targets in sorted(acct_tt.items()):
        if target_name in targets:
            c_own = raw_bal.get(name, 0)
            c_acc = accumulated.get(name, 0)
            c_val = c_own + c_acc  # value dumped into target
            c_nb = nb_map.get(name, 'D')
            c_sign = 1 if c_nb == 'D' else -1
            # Get report name for this account
            rpt_id = report_map.get(name)
            rpt_name = ''
            if rpt_id:
                rpt = get_report(rpt_id)
                if rpt:
                    rpt_name = rpt['name']
            contributors.append({
                'name': name,
                'normal_balance': c_nb,
                'own_raw': c_own,
                'accumulated': c_acc,
                'value_dumped': c_val,
                'display': c_val * sign,  # show in target's sign convention
                'targets': sorted(targets),
                'report': rpt_name,
            })

    return {
        'name': target_name,
        'normal_balance': target_nb,
        'own_raw': own_raw,
        'accumulated': acc_into,
        'merged': merged,
        'display': display,
        'date_from': date_from,
        'date_to': date_to,
        'contributors': sorted(contributors, key=lambda c: abs(c['value_dumped']), reverse=True),
        'feeds_into': sorted(acct_tt.get(target_name, set())),
    }

# ─── Trial Balance ────────────────────────────────────────────────
def get_trial_balance(as_of_date=None):
    with get_db() as db:
        accounts = db.execute("SELECT * FROM accounts WHERE account_type='posting' ORDER BY name").fetchall()
        result, total_dr, total_cr = [], 0, 0
        for acct in accounts:
            raw = get_account_balance(acct['id'], date_to=as_of_date)
            if raw == 0: continue
            sign = 1 if acct['normal_balance'] == 'D' else -1
            bal = raw * sign
            dr = bal if bal > 0 and acct['normal_balance'] == 'D' else (abs(bal) if bal < 0 and acct['normal_balance'] == 'C' else 0)
            cr = bal if bal > 0 and acct['normal_balance'] == 'C' else (abs(bal) if bal < 0 and acct['normal_balance'] == 'D' else 0)
            total_dr += dr; total_cr += cr
            result.append({'id': acct['id'], 'name': acct['name'], 'description': acct['description'],
                'normal_balance': acct['normal_balance'], 'account_number': acct['account_number'] or '',
                'balance': bal, 'debit': dr, 'credit': cr})
        return result, total_dr, total_cr

# ─── Search ───────────────────────────────────────────────────────
def search_transactions(query, limit=100):
    with get_db() as db:
        q = f"%{query}%"
        return db.execute("""
            SELECT DISTINCT t.id as txn_id, t.date, t.reference, t.description,
                   GROUP_CONCAT(DISTINCT a.name) as accounts,
                   (SELECT SUM(ABS(l2.amount)) FROM lines l2 WHERE l2.transaction_id=t.id AND l2.amount > 0) as total_amount
            FROM transactions t JOIN lines l ON l.transaction_id = t.id
            JOIN accounts a ON l.account_id = a.id
            WHERE t.description LIKE ? OR t.reference LIKE ? OR a.name LIKE ? OR l.description LIKE ?
            GROUP BY t.id ORDER BY t.date DESC LIMIT ?""", (q, q, q, q, limit)).fetchall()

# ─── Tax Codes ───────────────────────────────────────────────────
def get_tax_codes():
    with get_db() as db:
        return db.execute("SELECT * FROM tax_codes ORDER BY id").fetchall()

def get_tax_code(code_id):
    with get_db() as db:
        return db.execute("SELECT * FROM tax_codes WHERE id=?", (code_id,)).fetchone()

def save_tax_code(code_id, description, rate_percent, collected_account='', paid_account=''):
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO tax_codes(id, description, rate_percent, collected_account, paid_account) VALUES(?,?,?,?,?)",
            (code_id, description, rate_percent, collected_account, paid_account))

def delete_tax_code(code_id):
    with get_db() as db:
        db.execute("DELETE FROM tax_codes WHERE id=?", (code_id,))

# ─── Import Rules ────────────────────────────────────────────────
def get_import_rules():
    with get_db() as db:
        return db.execute("SELECT * FROM import_rules ORDER BY priority DESC, keyword").fetchall()

def save_import_rule(rule_id, keyword, account_name, tax_code='', priority=0, notes=''):
    with get_db() as db:
        if rule_id:
            db.execute("UPDATE import_rules SET keyword=?, account_name=?, tax_code=?, priority=?, notes=? WHERE id=?",
                (keyword, account_name, tax_code, priority, notes, rule_id))
        else:
            db.execute("INSERT INTO import_rules(keyword, account_name, tax_code, priority, notes) VALUES(?,?,?,?,?)",
                (keyword, account_name, tax_code, priority, notes))

def delete_import_rule(rule_id):
    with get_db() as db:
        db.execute("DELETE FROM import_rules WHERE id=?", (rule_id,))

def apply_rules(description, amount_cents):
    """Apply import rules to a description. Returns (account_name, tax_code, lines).
    lines is the list of (account_id, amount, desc) tuples ready for posting.
    If no rule matches, returns ('EX.SUSP', '', simple_lines)."""
    rules = get_import_rules()
    desc_lower = description.lower()
    
    matched_rule = None
    for rule in rules:
        if rule['keyword'].lower() in desc_lower:
            matched_rule = rule
            break  # rules are priority-sorted, first match wins
    
    if not matched_rule:
        return 'EX.SUSP', '', None
    
    acct_name = matched_rule['account_name']
    tax_id = matched_rule['tax_code']
    
    if tax_id:
        tc = get_tax_code(tax_id)
        if tc and tc['rate_percent'] > 0:
            rate = tc['rate_percent']
            # Amount is tax-inclusive. Split: tax = amount * rate / (100 + rate)
            tax_cents = round(abs(amount_cents) * rate / (100 + rate))
            net_cents = abs(amount_cents) - tax_cents
            
            # Determine which tax account to use
            if amount_cents > 0:
                # Money coming IN (revenue) → GST collected
                tax_acct = tc['collected_account'] or 'GST.OUT'
            else:
                # Money going OUT (expense) → GST paid (ITC)
                tax_acct = tc['paid_account'] or 'GST.IN'
            
            return acct_name, tax_id, {'net': net_cents, 'tax': tax_cents, 'tax_acct': tax_acct}
    
    return acct_name, tax_id, None
# ─── Formatting ───────────────────────────────────────────────────
def fmt_amount(cents):
    if cents == 0: return '—'
    neg = cents < 0; c = abs(cents)
    s = f"{c // 100:,}.{c % 100:02d}"
    return f"({s})" if neg else s

def fmt_amount_plain(cents):
    if cents == 0: return '0.00'
    neg = cents < 0; c = abs(cents)
    s = f"{c // 100:,}.{c % 100:02d}"
    return f"-{s}" if neg else s

def parse_amount(s):
    s = s.strip().replace(',', '').replace('$', '')
    neg = False
    if s.startswith('(') and s.endswith(')'): neg = True; s = s[1:-1]
    if s.startswith('-'): neg = True; s = s[1:]
    if s.endswith('-'): neg = True; s = s[:-1]
    s = s.strip()
    if not s: return 0
    if '.' in s:
        parts = s.split('.')
        dollars = int(parts[0] or '0')
        cp = parts[1][:2].ljust(2, '0')
        cents = dollars * 100 + int(cp)
    else:
        cents = int(s) * 100
    return -cents if neg else cents

def normalize_date(s):
    """Normalize a date string to YYYY-MM-DD. Handles OFX (YYYYMMDD), common date formats."""
    s = s.strip()
    if not s: return None
    if len(s) == 10 and s[4] == '-' and s[7] == '-': return s
    # OFX format: YYYYMMDD or YYYYMMDDHHMMSS
    if len(s) >= 8 and s[:8].isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    for fmt_str in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
                    '%m-%d-%Y', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y',
                    '%m/%d/%y', '%d/%m/%y'):
        try: return datetime.strptime(s, fmt_str).strftime('%Y-%m-%d')
        except ValueError: continue
    return None

def _ofx_sgml_to_xml(content):
    """Convert OFX SGML to valid XML by closing unclosed tags."""
    import re
    # Container/aggregate tags that wrap children — do NOT self-close these
    aggregates = {
        'OFX', 'SIGNONMSGSRSV1', 'SONRS', 'STATUS', 'FI',
        'BANKMSGSRSV1', 'STMTTRNRS', 'STMTRS', 'BANKACCTFROM',
        'BANKTRANLIST', 'STMTTRN', 'LEDGERBAL', 'AVAILBAL',
        'CREDITCARDMSGSRSV1', 'CCSTMTTRNRS', 'CCSTMTRS', 'CCACCTFROM',
    }
    agg_lower = {t.lower() for t in aggregates}

    def close_tags(match):
        tag = match.group(1)
        value = match.group(2).strip()
        if tag.lower() in agg_lower:
            return match.group(0)  # leave aggregates alone
        return f"<{tag}>{value}</{tag}>"

    # Match <TAG>value where value is non-empty text (not starting with <)
    return re.sub(r'<([A-Za-z0-9_.]+)>([^<\r\n]+)', close_tags, content)

def parse_ofx(file_path):
    """Parse an OFX/QBO file and return a list of row dicts for import_rows().

    Each dict has: date, description, amount_cents, reference (FITID).
    Uses stdlib only (xml.etree.ElementTree).
    """
    import xml.etree.ElementTree as ET

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Strip OFX headers (everything before <OFX>)
    idx = content.upper().find('<OFX>')
    if idx < 0:
        raise ValueError("Not a valid OFX file: no <OFX> tag found")
    content = content[idx:]

    # Try parsing as valid XML first, then fall back to SGML conversion
    root = None
    for attempt_content in [content, _ofx_sgml_to_xml(content)]:
        for suffix in ['', '</OFX>']:
            try:
                root = ET.fromstring(attempt_content + suffix)
                break
            except ET.ParseError:
                continue
        if root is not None:
            break
    if root is None:
        raise ValueError("Cannot parse OFX file: invalid XML/SGML structure")

    # Find all STMTTRN elements (works for both bank and credit card statements)
    transactions = root.iter('STMTTRN')

    rows = []
    for txn in transactions:
        dt_el = txn.find('DTPOSTED')
        amt_el = txn.find('TRNAMT')
        name_el = txn.find('NAME')
        memo_el = txn.find('MEMO')
        fitid_el = txn.find('FITID')

        if dt_el is None or amt_el is None:
            continue

        # Build description from NAME + MEMO
        name = (name_el.text or '').strip() if name_el is not None else ''
        memo = (memo_el.text or '').strip() if memo_el is not None else ''
        if memo and memo.lower() != name.lower():
            description = f"{name} — {memo}" if name else memo
        else:
            description = name or memo

        if not description:
            continue

        amount_cents = parse_amount(amt_el.text)
        fitid = (fitid_el.text or '').strip() if fitid_el is not None else ''

        rows.append({
            'date': (dt_el.text or '').strip(),
            'description': description,
            'amount_cents': amount_cents,
            'reference': fitid,
        })

    if not rows:
        raise ValueError("No transactions found in OFX file")

    return rows

def import_rows(bank_account_id, rows):
    """Shared posting loop for CSV and OFX imports.

    Args:
        bank_account_id: int — the bank account to post against
        rows: list of dicts with keys: date, description, amount_cents, reference (optional)

    Returns:
        dict with: rows_processed, posted, skipped, to_suspense, errors, possible_duplicates
    """
    posted = 0
    skipped = 0
    suspense = 0
    errors = []
    possible_duplicates = []
    lock = get_meta('lock_date', '')

    # Pre-scan for possible duplicates: existing transactions on the bank account.
    # Two detection methods:
    #   1. FITID (reference) — deterministic for OFX imports. Same FITID = same txn.
    #   2. Date + amount — soft match for CSV imports (warns but still posts).
    existing = set()
    existing_refs = set()
    fitid_skipped = 0
    with get_db() as db:
        for r in db.execute(
                "SELECT t.date, t.reference, l.amount FROM lines l "
                "JOIN transactions t ON l.transaction_id = t.id "
                "WHERE l.account_id = ?", (bank_account_id,)).fetchall():
            existing.add((r['date'], r['amount']))
            ref = r['reference']
            if ref and ref.strip():
                existing_refs.add(ref.strip())

    for row_num, row in enumerate(rows, start=1):
        row_date = normalize_date(row['date'])
        row_desc = row['description']
        amount_cents = row['amount_cents']
        reference = row.get('reference', '')

        if not row_desc:
            errors.append({'row': row_num, 'reason': 'Missing description'})
            skipped += 1
            continue

        if not row_date:
            errors.append({'row': row_num, 'reason': f"Bad date '{row['date']}'"})
            skipped += 1
            continue

        if lock and row_date <= lock:
            errors.append({'row': row_num, 'reason': f'Before lock date {lock}'})
            skipped += 1
            continue

        ceiling = get_meta('fy_end_date', '')
        if ceiling and row_date > ceiling:
            errors.append({'row': row_num, 'reason': f'After fiscal year end {ceiling}'})
            skipped += 1
            continue

        if amount_cents == 0:
            errors.append({'row': row_num, 'reason': 'Zero amount'})
            skipped += 1
            continue

        # FITID duplicate detection: if reference matches an existing transaction, skip entirely.
        # FITID is a unique bank-assigned ID — same FITID = guaranteed duplicate.
        if reference and reference.strip() and reference.strip() in existing_refs:
            fitid_skipped += 1
            skipped += 1
            continue

        # Soft duplicate detection: check if this date+amount already exists on the bank account
        if (row_date, amount_cents) in existing:
            possible_duplicates.append({
                'row': row_num, 'date': row_date,
                'amount': amount_cents, 'description': row_desc[:60]})

        matched_acct, tax_code, tax_info = apply_rules(row_desc, amount_cents)

        target_acct = get_account_by_name(matched_acct)
        if not target_acct:
            errors.append({'row': row_num, 'reason': f"Account '{matched_acct}' not found"})
            skipped += 1
            continue

        if matched_acct == 'EX.SUSP':
            suspense += 1

        try:
            if tax_info and tax_info.get('tax'):
                tax_acct = get_account_by_name(tax_info['tax_acct'])
                if not tax_acct:
                    add_simple_transaction(
                        row_date, reference, row_desc,
                        target_acct['id'] if amount_cents < 0 else bank_account_id,
                        bank_account_id if amount_cents < 0 else target_acct['id'],
                        abs(amount_cents))
                else:
                    net = tax_info['net']
                    tax = tax_info['tax']
                    if amount_cents < 0:
                        txn_lines = [
                            (target_acct['id'], net, row_desc),
                            (tax_acct['id'], tax, f"{tax_code} on {row_desc[:30]}"),
                            (bank_account_id, -(net + tax), row_desc),
                        ]
                    else:
                        txn_lines = [
                            (bank_account_id, net + tax, row_desc),
                            (target_acct['id'], -net, row_desc),
                            (tax_acct['id'], -tax, f"{tax_code} on {row_desc[:30]}"),
                        ]
                    add_transaction(row_date, reference, row_desc, txn_lines)
            else:
                if amount_cents < 0:
                    add_simple_transaction(
                        row_date, reference, row_desc,
                        target_acct['id'], bank_account_id, abs(amount_cents))
                else:
                    add_simple_transaction(
                        row_date, reference, row_desc,
                        bank_account_id, target_acct['id'], abs(amount_cents))
            posted += 1
            # Track for within-batch duplicate detection
            existing.add((row_date, amount_cents))
            if reference and reference.strip():
                existing_refs.add(reference.strip())
        except ValueError as e:
            errors.append({'row': row_num, 'reason': str(e)})
            skipped += 1

    result = {
        'rows_processed': len(rows),
        'posted': posted,
        'skipped': skipped,
        'fitid_skipped': fitid_skipped,
        'to_suspense': suspense,
        'errors': errors[:20] if errors else [],
        'possible_duplicates': possible_duplicates[:20] if possible_duplicates else [],
    }
    return result

# ─── Report Chain Validation ──────────────────────────────────────
def validate_report_chain():
    """Validate the total-to chain across all reports.

    Checks:
      1. Every total report item has an account_id linked
      2. IS chain reaches RE on the BS (NI → RE.CLOSE → RE)
      3. RE.OFS and RE.OPEN accounts exist
      4. BS balances (Total Assets = Total L&E)
      5. BS RE vs IS RE.CLOSE cross-check
      6. No orphan total accounts (accounts referenced by total_to but not on any report)

    Returns: list of {level: 'error'|'warning', message: str}
    """
    issues = []

    all_items = get_all_report_items()
    if not all_items:
        issues.append({'level': 'error', 'message': 'No report items found. Run create_starter_books() first.'})
        return issues

    # 1. Total items without account_id
    for it in all_items:
        if it['item_type'] == 'total' and not it['account_id']:
            rpt = it['report_id']
            issues.append({'level': 'error',
                'message': f"Total item '{it['description']}' (report {rpt}) has no account_id linked. "
                           f"It will always show zero."})

    # 2. Collect the total-to graph
    tt_fields = ['total_to_1','total_to_2','total_to_3','total_to_4','total_to_5']
    # Map: account_name -> set of target names
    feeds_into = {}
    all_acct_names = set()
    for it in all_items:
        name = it['acct_name'] if 'acct_name' in it.keys() else None
        if not name:
            continue
        all_acct_names.add(name)
        for ttf in tt_fields:
            target = it[ttf] if ttf in it.keys() else ''
            if target:
                feeds_into.setdefault(name, set()).add(target)
                all_acct_names.add(target)

    # 3. Check IS → BS chain: need path from revenue/expense totals to RE on BS
    bs_report = find_report_by_name('BS')
    is_report = find_report_by_name('IS')

    # Check RE.OPEN and RE.OFS exist
    re_open = get_account_by_name('RE.OPEN')
    re_ofs = get_account_by_name('RE.OFS')
    if not re_open:
        issues.append({'level': 'error',
            'message': "RE.OPEN account missing. Required for year-end closing (ye command)."})
    if not re_ofs:
        issues.append({'level': 'error',
            'message': "RE.OFS account missing. Required for perpetual retained earnings."})

    # Check RE total account exists and is on BS
    re_acct = get_account_by_name('RE')
    if not re_acct:
        issues.append({'level': 'error',
            'message': "RE total account missing. Retained earnings has no accumulator on BS."})
    elif re_acct['account_type'] != 'total':
        issues.append({'level': 'warning',
            'message': "RE is a posting account, not a total. It won't accumulate RE.CLOSE chain."})

    # Check RE.CLOSE exists and chains to RE
    re_close = get_account_by_name('RE.CLOSE')
    if not re_close:
        issues.append({'level': 'error',
            'message': "RE.CLOSE total account missing. IS net income cannot flow to BS."})
    elif 'RE' not in feeds_into.get('RE.CLOSE', set()):
        issues.append({'level': 'error',
            'message': "RE.CLOSE does not total-to RE. IS net income won't reach the BS."})

    # Check NI exists and chains to RE.CLOSE
    ni_acct = get_account_by_name('NI')
    if not ni_acct:
        # Check for NETINC as alternative
        ni_acct = get_account_by_name('NETINC')
        if not ni_acct:
            issues.append({'level': 'error',
                'message': "NI (or NETINC) total account missing. No net income accumulator."})

    # Check that at least one IS total feeds into NI chain
    if is_report:
        is_items = get_report_items(is_report['id'])
        is_totals = [it['acct_name'] for it in is_items
                     if it['item_type'] == 'total' and it['acct_name']]
        # Trace from each IS total to see if it reaches RE
        def reaches(name, target, visited=None):
            if visited is None:
                visited = set()
            if name in visited:
                return False
            visited.add(name)
            targets = feeds_into.get(name, set())
            if target in targets:
                return True
            return any(reaches(t, target, visited) for t in targets)

        chain_ok = any(reaches(t, 'RE') for t in is_totals)
        if not chain_ok:
            issues.append({'level': 'error',
                'message': "IS total-to chain does not reach RE on BS. "
                           "Net income won't flow to equity. "
                           "Need: IS totals → NI → RE.CLOSE → RE."})

    # Check RE.OFS feeds into RE
    if re_ofs and 'RE' not in feeds_into.get('RE.OFS', set()):
        issues.append({'level': 'warning',
            'message': "RE.OFS does not total-to RE. Year-end offset won't reach BS equity."})

    # 4. Check BS balances
    if bs_report:
        data = compute_report_column(bs_report['id'])
        ta_bal = tle_bal = None
        for item, bal in data:
            name = item.get('acct_name')
            if name == 'TA':
                ta_bal = bal
            elif name == 'TLE' or name == 'TL':
                tle_bal = bal
        if ta_bal is not None and tle_bal is not None:
            diff = ta_bal - tle_bal
            if diff != 0:
                issues.append({'level': 'error',
                    'message': f"BS out of balance: Total Assets ({fmt_amount(ta_bal)}) != "
                               f"Liabilities & Equity ({fmt_amount(tle_bal)}). "
                               f"Difference: {fmt_amount(diff)}."})
        elif ta_bal is None:
            issues.append({'level': 'warning',
                'message': "Cannot find TA (Total Assets) on BS to verify balance."})

    # 5. BS RE vs IS RE.CLOSE cross-check
    #    Computes both values for the current FY and flags any discrepancy.
    #    This catches duplicate transactions, chain wiring mismatches, and
    #    conversion artifacts — the single most valuable data-integrity check.
    if bs_report and is_report and re_acct:
        try:
            # Determine current FY dates
            fye_md = get_meta('fiscal_year_end', '')
            fy_year = get_meta('fiscal_year', '')
            if fye_md and fy_year:
                fye_m, fye_d = int(fye_md.split('-')[0]), int(fye_md.split('-')[1])
                fy_end = f"{fy_year}-{fye_m:02d}-{fye_d:02d}"
                # FY start = day after previous FY end
                if fye_m == 12 and fye_d == 31:
                    fy_start = f"{int(fy_year)}-01-01"
                else:
                    from calendar import monthrange
                    _, last = monthrange(2000, fye_m)
                    if fye_d >= last:
                        sm = fye_m + 1 if fye_m < 12 else 1
                        sy = int(fy_year) if fye_m < 12 else int(fy_year)
                        fy_start = f"{sy}-{sm:02d}-01"
                    else:
                        sy = int(fy_year) - 1 if fye_m < 12 or fye_d < 31 else int(fy_year)
                        fy_start = f"{int(fy_year)-1}-{fye_m:02d}-{fye_d+1:02d}"
                    # Simpler: FY start is 1 day after last year's FY end
                    from datetime import date as _date, timedelta as _td
                    prev_fy_end = _date(int(fy_year) - 1, fye_m, fye_d)
                    fy_start = (prev_fy_end + _td(days=1)).isoformat()

                # BS RE: all-time up to FY end
                bs_data = compute_report_column(bs_report['id'], date_to=fy_end)
                bs_re_val = None
                for item, bal in bs_data:
                    if item.get('acct_name') == 'RE':
                        bs_re_val = bal
                        break

                # IS RE.CLOSE: for the FY period
                is_data = compute_report_column(is_report['id'],
                                                date_from=fy_start, date_to=fy_end)
                is_reclose_val = None
                # Try RE.CLOSE first, fall back to any account containing 'RE' at IS tail
                for item, bal in is_data:
                    if item.get('acct_name') == 'RE.CLOSE':
                        is_reclose_val = bal
                        break
                if is_reclose_val is None:
                    for item, bal in is_data:
                        if item.get('acct_name') == 'RE':
                            is_reclose_val = bal
                            break

                if bs_re_val is not None and is_reclose_val is not None:
                    diff = bs_re_val - is_reclose_val
                    if diff != 0:
                        issues.append({'level': 'error',
                            'message': f"BS Retained Earnings ({fmt_amount(bs_re_val)}) != "
                                       f"IS Closing RE ({fmt_amount(is_reclose_val)}) "
                                       f"for FY ending {fy_end}. "
                                       f"Difference: {fmt_amount(diff)}. "
                                       f"Check for duplicate transactions or chain wiring issues."})
                elif bs_re_val is None:
                    issues.append({'level': 'warning',
                        'message': "Cannot find RE on BS to cross-check against IS."})
                elif is_reclose_val is None:
                    issues.append({'level': 'warning',
                        'message': "Cannot find RE.CLOSE (or RE) on IS to cross-check against BS."})
        except (ValueError, IndexError, TypeError):
            pass  # FY dates not configured — skip this check

    # 6. Orphan total-to targets (referenced but not on any report)
    on_report = set()
    for it in all_items:
        if it['acct_name']:
            on_report.add(it['acct_name'])
    for name, targets in feeds_into.items():
        for t in targets:
            if t not in on_report:
                acct = get_account_by_name(t)
                if not acct:
                    issues.append({'level': 'error',
                        'message': f"'{name}' total-to '{t}' but account '{t}' does not exist."})
                else:
                    issues.append({'level': 'warning',
                        'message': f"'{name}' total-to '{t}' but '{t}' is not on any report. "
                                   f"Balance will accumulate but never display."})

    if not issues:
        issues.append({'level': 'ok', 'message': 'Report chain is valid. BS balances.'})

    return issues


# ─── Rollforward ─────────────────────────────────────────────────
def rollforward(ye_date):
    """Year-end rollforward. Posts closing RE offset entry, sets lock, advances ceiling.

    Reads RE.CLOSE (not RE from BS) to get the correct closing retained earnings.
    Posts Dr RE.OFS / Cr RE.OPEN dated first day of new fiscal year.
    Sets lock_date = ye_date, advances fy_end_date to next year.

    Returns dict with: txn_id, closing_re, new_fy_start, lock_date, fy_end_date
    """
    from datetime import timedelta

    # Validate date
    try:
        ye_dt = datetime.strptime(ye_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: '{ye_date}'. Use YYYY-MM-DD.")

    # Find required accounts
    re_open = get_account_by_name('RE.OPEN')
    if not re_open:
        raise ValueError("RE.OPEN account not found. Required for rollforward.")

    re_ofs_acct = get_account_by_name('RE.OFS')
    if not re_ofs_acct:
        raise ValueError("RE.OFS account not found. Required for rollforward.")

    # Read RE.CLOSE from the IS report (where the RE chain lives)
    is_report = find_report_by_name('IS')
    if not is_report:
        raise ValueError("No IS (Income Statement) report found. Required for rollforward.")

    all_items = get_all_report_items()
    display_items = get_report_items(is_report['id'])
    data = compute_report_column(is_report['id'], date_to=ye_date,
                                  _display_items=display_items, _all_items=all_items)

    # Find the RE.CLOSE total in the computed IS data
    re_close_balance = None
    for item, balance in data:
        if item.get('acct_name') == 'RE.CLOSE':
            re_close_balance = balance
            break

    if re_close_balance is None:
        raise ValueError("RE.CLOSE total not found in IS report. "
                         "The report chain must include RE.CLOSE.")

    if re_close_balance == 0:
        raise ValueError("RE.CLOSE balance is zero — nothing to roll forward.")

    # Convert display balance to raw amount for posting
    re_close_acct = get_account_by_name('RE.CLOSE')
    if re_close_acct:
        sign = 1 if re_close_acct['normal_balance'] == 'D' else -1
        raw_re = re_close_balance * sign
    else:
        raw_re = -re_close_balance

    # Compute new fiscal year start and post the entry
    new_fy_start = (ye_dt + timedelta(days=1)).strftime('%Y-%m-%d')
    fy_year = ye_dt.strftime('%Y')
    desc = f"{fy_year} Closing RE"

    ofs_raw = -raw_re   # RE.OFS is D-normal, gets debit
    open_raw = raw_re   # RE.OPEN is C-normal, gets credit

    lines = [
        (re_ofs_acct['id'], ofs_raw, desc),
        (re_open['id'], open_raw, desc)
    ]
    txn_id = add_transaction(new_fy_start, 'YE-OFS', desc, lines, _bypass_ceiling=True)

    # Set lock date
    set_meta('lock_date', ye_date)

    # Advance ceiling to next fiscal year
    fye_md = get_meta('fiscal_year_end', '12-31')
    new_fy_year = (ye_dt + timedelta(days=1)).strftime('%Y')
    fy_mm, fy_dd = fye_md.split('-')
    new_ceiling = f"{new_fy_year}-{fy_mm}-{fy_dd}"
    set_meta('fy_end_date', new_ceiling)
    set_meta('fiscal_year', new_fy_year)

    return {
        'txn_id': txn_id,
        'closing_re': re_close_balance,
        'raw_re': raw_re,
        'ofs_raw': ofs_raw,
        'open_raw': open_raw,
        'new_fy_start': new_fy_start,
        'lock_date': ye_date,
        'fy_end_date': new_ceiling,
        'fiscal_year': new_fy_year,
        'description': desc,
    }


# ─── Starter Template ─────────────────────────────────────────────
def create_starter_books(path, company_name='My Company', fiscal_ye='12-31'):
    init_db(path)
    set_meta('company_name', company_name)
    set_meta('fiscal_year_end', fiscal_ye)

    # Compute and store the full fiscal year end date (ceiling)
    today = date.today()
    fy_mm, fy_dd = fiscal_ye.split('-')
    fy_end = date(today.year, int(fy_mm), int(fy_dd))
    if today > fy_end:
        fy_end = date(today.year + 1, int(fy_mm), int(fy_dd))
    set_meta('fy_end_date', fy_end.strftime('%Y-%m-%d'))
    set_meta('fiscal_year', str(fy_end.year))

    bs = add_report('BS', 'Balance Sheet', 10)
    is_ = add_report('IS', 'Income Statement', 20)
    aje = add_report('AJE', 'Adjusting Journal Entries', 30)
    trx = add_report('TRX', 'Transactions Journal', 40)
    reofs = add_report('RE.OFS', 'Retained Earnings Offset', 50)

    a = {}
    def ac(name, bal, desc, atype='posting'):
        a[name] = add_account(name, bal, desc, atype)

    # ── BS accounts ──
    ac('CASH','D','Petty Cash'); ac('BANK.CHQ','D','Bank - Chequing'); ac('BANK.SAV','D','Bank - Savings')
    ac('TOTBANK','D','Total Bank Accounts','total')
    ac('AR','D','Accounts Receivable'); ac('AR.TOT','D','Total AR','total')
    ac('PREPAIDS','D','Prepaid Expenses'); ac('DEP','D','Deposits')
    ac('CA','D','Total Current Assets','total')
    ac('EQUIP','D','Equipment'); ac('FURN','D','Furniture'); ac('COMP','D','Computer Equipment')
    ac('TOTFA','D','Total Capital Assets','total')
    ac('EQUIP.DEP','C','Accum Amort - Equipment'); ac('FURN.DEP','C','Accum Amort - Furniture'); ac('COMP.DEP','C','Accum Amort - Computer')
    ac('TOTDEP','C','Total Accum Amortization','total')
    ac('NETFA','D','Net Capital Assets','total')
    ac('TA','D','TOTAL ASSETS','total')
    ac('AP','C','Accounts Payable'); ac('AP.CC','C','Credit Card Payable')
    ac('GST.OUT','C','GST Collected'); ac('GST.IN','D','GST Paid (ITCs)')
    ac('GST.REMIT','C','GST Remittance'); ac('GST.PAY','C','GST Payable')
    ac('TOTGST','C','Total GST','total')
    ac('FEDTAX','C','Federal Tax Payable'); ac('PROTAX','C','Provincial Tax Payable')
    ac('TOT.TAX','C','Total Tax Payable','total')
    ac('CL','C','Total Current Liabilities','total')
    ac('LOAN','C','Bank Loan'); ac('SH.LOAN','C','Shareholder Loan'); ac('TOTTERM','C','Total LT Debt','total')
    ac('LTL','C','Total Long-Term Liabilities','total')
    ac('CAPITAL','C','Share Capital'); ac('RE','C','Retained Earnings','total')
    ac('EQ','C','Total Equity','total')
    ac('TL','C','TOTAL LIABILITIES & EQUITY','total')

    # ── IS accounts ──
    ac('REV','C','Revenue - Sales'); ac('REV.SVC','C','Revenue - Services')
    ac('TOTREV','C','Total Revenue','total')
    ac('CS.MAT','D','Cost of Sales - Materials'); ac('CS.SUB','D','Cost of Sales - Subcontractors'); ac('CS.SHIP','D','Cost of Sales - Shipping')
    ac('GROSS','C','Gross Profit','total')
    ac('EX.SAL','D','Salaries & Wages'); ac('EX.RENT','D','Rent'); ac('EX.OFFICE','D','Office & General')
    ac('EX.COMP','D','Computer & IT'); ac('EX.ADV','D','Advertising'); ac('EX.INS','D','Insurance')
    ac('EX.PHONE','D','Telephone'); ac('EX.TRAVEL','D','Travel'); ac('EX.MEALS','D','Meals & Entertainment')
    ac('EX.AUTO','D','Vehicle'); ac('EX.POST','D','Postage & Courier'); ac('EX.FEES','D','Professional Fees')
    ac('EX.SC','D','Service Charges'); ac('EX.AMORT','D','Amortization'); ac('EX.SUSP','D','Suspense')
    ac('TOTEX','D','Total Operating Expenses','total')
    ac('OPINC','C','Operating Income','total')
    ac('EX.LIFE','D','Life Insurance'); ac('EX.LTINT','D','Interest on LT Debt'); ac('EX.INTAX','D','Income Tax Expense')
    ac('TAXINC','C','Income Before Taxes','total'); ac('NETINC','C','Net Income','total')
    ac('NI','C','Net Income for Year','total')
    ac('RE.OPEN','C','Retained Earnings - Open'); ac('DIVPAID','C','Dividends Paid')
    ac('RE.CLOSE','C','Retained Earnings - Close','total')

    # ── BS report items ──
    p = [0]
    def bi(itype, desc='', an=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(bs, itype, desc, a.get(an), ind, p[0], tt1, sep_style=sep)

    bi('label','CURRENT ASSETS')
    bi('label','Bank Accounts:')
    bi('account','','CASH',2,'TOTBANK'); bi('account','','BANK.CHQ',2,'TOTBANK'); bi('account','','BANK.SAV',2,'TOTBANK')
    bi('separator',sep='single'); bi('total','','TOTBANK',3,'CA')
    bi('label','')
    bi('label','Accounts Receivable:')
    bi('account','','AR',2,'AR.TOT')
    bi('separator',sep='single'); bi('total','','AR.TOT',3,'CA')
    bi('label','')
    bi('label','Other Current Assets:')
    bi('account','','PREPAIDS',2,'CA'); bi('account','','DEP',2,'CA')
    bi('separator',sep='single'); bi('total','Total Current Assets','CA',3,'TA')
    bi('separator',sep='single'); bi('label','')
    bi('label','Capital Assets')
    bi('account','','EQUIP',2,'TOTFA'); bi('account','','FURN',2,'TOTFA'); bi('account','','COMP',2,'TOTFA')
    bi('separator',sep='single'); bi('total','','TOTFA',3,'NETFA')
    bi('label','')
    bi('label','Accumulated Amortization')
    bi('account','','EQUIP.DEP',2,'TOTDEP'); bi('account','','FURN.DEP',2,'TOTDEP'); bi('account','','COMP.DEP',2,'TOTDEP')
    bi('separator',sep='single'); bi('total','','TOTDEP',3,'NETFA')
    bi('separator',sep='single'); bi('total','Net Capital Assets','NETFA',3,'TA')
    bi('separator',sep='single'); bi('label','')
    bi('total','TOTAL ASSETS','TA',0); bi('separator',sep='double'); bi('label','')
    bi('label','CURRENT LIABILITIES')
    bi('account','','AP',2,'CL'); bi('account','','AP.CC',2,'CL')
    bi('label',''); bi('label','GST:')
    bi('account','','GST.OUT',2,'TOTGST'); bi('account','','GST.IN',2,'TOTGST')
    bi('account','','GST.REMIT',2,'TOTGST'); bi('account','','GST.PAY',2,'TOTGST')
    bi('separator',sep='single'); bi('total','','TOTGST',3,'CL')
    bi('label','')
    bi('account','','FEDTAX',2,'TOT.TAX'); bi('account','','PROTAX',2,'TOT.TAX')
    bi('separator',sep='single'); bi('total','','TOT.TAX',3,'CL')
    bi('separator',sep='single'); bi('total','Total Current Liabilities','CL',3,'TL')
    bi('separator',sep='single'); bi('label','')
    bi('label','Long-Term Liabilities')
    bi('account','','LOAN',2,'TOTTERM')
    bi('account','','SH.LOAN',2,'TOTTERM')
    bi('separator',sep='single'); bi('total','','TOTTERM',3,'LTL')
    bi('total','Total Long-Term Liabilities','LTL',3,'TL')
    bi('separator',sep='single'); bi('label','')
    bi('label','Equity')
    bi('account','','CAPITAL',2,'EQ'); bi('account','','RE',2,'EQ')
    bi('separator',sep='single'); bi('total','Total Equity','EQ',3,'TL')
    bi('separator',sep='single'); bi('label','')
    bi('total','TOTAL LIABILITIES & EQUITY','TL',0); bi('separator',sep='double')

    # ── IS report items ──
    p[0] = 0
    def ii(itype, desc='', an=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(is_, itype, desc, a.get(an), ind, p[0], tt1, sep_style=sep)

    ii('label','REVENUE')
    ii('account','','REV',2,'TOTREV'); ii('account','','REV.SVC',2,'TOTREV')
    ii('separator',sep='single'); ii('total','Total Revenue','TOTREV',3,'GROSS'); ii('label','')
    ii('label','COST OF SALES')
    ii('account','','CS.MAT',2,'GROSS'); ii('account','','CS.SUB',2,'GROSS'); ii('account','','CS.SHIP',2,'GROSS')
    ii('separator',sep='single'); ii('label','')
    ii('total','Gross Profit','GROSS',3,'OPINC'); ii('separator',sep='single'); ii('label','')
    ii('label','EXPENSES')
    ii('account','','EX.SAL',2,'TOTEX'); ii('account','','EX.RENT',2,'TOTEX'); ii('account','','EX.OFFICE',2,'TOTEX')
    ii('account','','EX.COMP',2,'TOTEX'); ii('account','','EX.ADV',2,'TOTEX'); ii('account','','EX.INS',2,'TOTEX')
    ii('account','','EX.PHONE',2,'TOTEX'); ii('account','','EX.TRAVEL',2,'TOTEX'); ii('account','','EX.MEALS',2,'TOTEX')
    ii('account','','EX.AUTO',2,'TOTEX'); ii('account','','EX.POST',2,'TOTEX'); ii('account','','EX.FEES',2,'TOTEX')
    ii('account','','EX.SC',2,'TOTEX'); ii('account','','EX.AMORT',2,'TOTEX'); ii('account','','EX.SUSP',2,'TOTEX')
    ii('separator',sep='single'); ii('total','Total Operating Expenses','TOTEX',3,'OPINC')
    ii('separator',sep='single'); ii('label','')
    ii('total','Operating Income','OPINC',3,'TAXINC'); ii('separator',sep='single'); ii('label','')
    ii('label','Other Items:')
    ii('account','','EX.LIFE',2,'TAXINC'); ii('account','','EX.LTINT',2,'TAXINC')
    ii('separator',sep='single')
    ii('total','Income Before Taxes','TAXINC',3,'NETINC'); ii('label','')
    ii('account','','EX.INTAX',2,'NETINC')
    ii('separator',sep='single'); ii('total','Net Income (Loss)','NETINC',3,'NI'); ii('separator',sep='double')
    ii('label','')
    ii('account','Retained Earnings - Open','RE.OPEN',2,'RE.CLOSE')
    ii('total','Net Income for Year','NI',2,'RE.CLOSE')
    ii('account','Dividends Paid','DIVPAID',2,'RE.CLOSE')
    ii('separator',sep='single'); ii('total','Retained Earnings - Close','RE.CLOSE',3,'RE'); ii('separator',sep='double')

    # ── RE.OFS report items (Retained Earnings Offset Journal) ──
    # RE.OFS is a D-normal posting account that totals to RE.
    # This allows the perpetual total-to chain to work: the debit in RE.OFS
    # offsets the credit in RE.OPEN, keeping the BS balanced across fiscal years.
    ac('RE.OFS','D','Annual Opening RE Offset')
    
    p[0] = 0
    def ri(itype, desc='', an=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(reofs, itype, desc, a.get(an), ind, p[0], tt1, sep_style=sep)

    ri('label','RETAINED EARNINGS OFFSET')
    ri('label','')
    ri('account','Retained Earnings - Open','RE.OPEN',1)
    ri('account','Annual Opening RE Offset','RE.OFS',1,'RE')
    ri('label','')
    ri('separator',sep='double')

    # ── PY.CLOSE account — for balance-sheet-only imports ──
    # When importing only PY balance sheet amounts (no income history),
    # post all PY closing totals against PY.CLOSE. The unreconciled
    # difference is normal — PY.CLOSE total-to RE makes it flow correctly.
    ac('PY.CLOSE','C','Prior Year Closing Balance')

    # ── TRX report items (PY closing journal) ──
    p[0] = 0
    def ti(itype, desc='', an=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(trx, itype, desc, a.get(an), ind, p[0], tt1, sep_style=sep)

    ti('label','PRIOR YEAR CLOSING')
    ti('label','')
    ti('account','Prior Year Closing Balance','PY.CLOSE',1,'RE')
    ti('label','')
    ti('separator',sep='double')

    # AJE starts empty — user builds it with backslash menu

    # ── Default import rules (80/20 common Canadian expenses, 5% GST ITCs) ──
    rules = [
        # Revenue / deposits
        ('E-TRANSFER DEPOSIT','REV.SVC','E', 15, 'Client deposits'),
        ('DEPOSIT',    'REV.SVC',   'E',  3, 'Generic deposits'),
        ('PAYMENT RECEIVED','REV.SVC','E', 15, ''),
        ('TRANSFER IN','BANK.SAV',  'E',  12, 'Inter-bank transfer'),
        ('TRANSFER OUT','BANK.SAV', 'E',  12, 'Inter-bank transfer'),
        ('TFR FROM SAV','BANK.SAV', 'E',  12, 'Inter-bank transfer'),
        ('TFR TO SAV', 'BANK.SAV',  'E',  12, 'Inter-bank transfer'),
        # Advertising
        ('FACEBOOK',   'EX.ADV',    'G5', 5,  ''),
        ('GOOGLE ADS', 'EX.ADV',    'G5', 10, ''),
        ('META',       'EX.ADV',    'G5', 5,  ''),
        # Banking / service charges
        ('BANK FEE',   'EX.SC',     'E',  10, ''),
        ('INTEREST CHARGE','EX.SC', 'E',  10, ''),
        ('MONTHLY FEE','EX.SC',     'E',  10, ''),
        ('NSF',        'EX.SC',     'E',  10, ''),
        ('OVERDRAFT',  'EX.SC',     'E',  10, ''),
        ('SERVICE CHARGE','EX.SC',  'E',  10, ''),
        # Insurance
        ('INSURANCE',  'EX.INS',    'E',  5,  ''),
        ('INTACT',     'EX.INS',    'E',  10, ''),
        ('WAWANESA',   'EX.INS',    'E',  10, ''),
        # Loans
        ('LOAN ADVANCE','LOAN',     'E',  15, 'Bank loan advance'),
        ('LOAN PAYMENT','LOAN',     'E',  15, 'Bank loan payment'),
        ('SH ADVANCE', 'SH.LOAN',   'E',  15, 'Shareholder advance'),
        ('SH DRAW',    'SH.LOAN',   'E',  15, 'Shareholder draw'),
        # Meals
        ('DOORDASH',   'EX.MEALS',  'G5', 5,  ''),
        ('MCDONALD',   'EX.MEALS',  'G5', 5,  ''),
        ('SKIP THE',   'EX.MEALS',  'G5', 5,  ''),
        ('STARBUCKS',  'EX.MEALS',  'G5', 5,  ''),
        ('TIM HORTON', 'EX.MEALS',  'G5', 5,  ''),
        ('UBER EATS',  'EX.MEALS',  'G5', 5,  ''),
        # Office & supplies
        ('AMAZON',     'EX.OFFICE', 'G5', 10, ''),
        ('COSTCO',     'EX.OFFICE', 'G5', 5,  ''),
        ('DOLLARAMA',  'EX.OFFICE', 'G5', 5,  ''),
        ('OFFICE DEPOT','EX.OFFICE','G5', 10, ''),
        ('STAPLES',    'EX.OFFICE', 'G5', 10, ''),
        ('WALMART',    'EX.OFFICE', 'G5', 5,  ''),
        # Payroll
        ('CRA',        'FEDTAX',    'E',  5,  'May be payroll remit or tax'),
        ('PAYROLL',    'EX.SAL',    'E',  5,  ''),
        # Professional fees
        ('LEGAL',      'EX.FEES',   'G5', 5,  ''),
        # Rent
        ('RENT',       'EX.RENT',   'E',  5,  ''),
        # Shipping
        ('CANADA POST','EX.POST',   'G5', 10, ''),
        ('FEDEX',      'EX.POST',   'G5', 10, ''),
        ('PUROLATOR',  'EX.POST',   'G5', 10, ''),
        ('UPS',        'EX.POST',   'G5', 10, ''),
        # Technology
        ('ADOBE',      'EX.COMP',   'G5', 10, ''),
        ('APPLE',      'EX.COMP',   'G5', 5,  ''),
        ('DROPBOX',    'EX.COMP',   'G5', 10, ''),
        ('GOOGLE',     'EX.COMP',   'G5', 10, ''),
        ('INTUIT',     'EX.COMP',   'G5', 10, ''),
        ('MICROSOFT',  'EX.COMP',   'G5', 10, ''),
        ('ZOOM',       'EX.COMP',   'G5', 10, ''),
        # Telephone
        ('BELL',       'EX.PHONE',  'G5', 10, ''),
        ('FIDO',       'EX.PHONE',  'G5', 10, ''),
        ('ROGERS',     'EX.PHONE',  'G5', 10, ''),
        ('SHAW',       'EX.PHONE',  'G5', 10, ''),
        ('TELUS',      'EX.PHONE',  'G5', 10, ''),
        # Travel
        ('AIR CANADA', 'EX.TRAVEL', 'E',  10, ''),
        ('AIRBNB',     'EX.TRAVEL', 'G5', 5,  ''),
        ('HOTEL',      'EX.TRAVEL', 'G5', 5,  ''),
        ('WESTJET',    'EX.TRAVEL', 'E',  10, ''),
        # Utilities
        ('ENBRIDGE',   'EX.OFFICE', 'G5', 10, 'Natural Gas'),
        ('HYDRO',      'EX.OFFICE', 'G5', 10, 'Hydro / Electric'),
        # Vehicle / fuel
        ('CANADIAN TIRE','EX.AUTO', 'G5', 5,  ''),
        ('ESSO',       'EX.AUTO',   'G5', 10, ''),
        ('PARKING',    'EX.AUTO',   'E',  5,  ''),
        ('PETRO',      'EX.AUTO',   'G5', 10, ''),
        ('PIONEER',    'EX.AUTO',   'G5', 10, ''),
        ('SHELL',      'EX.AUTO',   'G5', 10, ''),
        ('ULTRAMAR',   'EX.AUTO',   'G5', 10, ''),
    ]
    for kw, acct, tax, pri, notes in rules:
        save_import_rule(None, kw, acct, tax, pri, notes)

    # Default tax codes for Canada
    save_tax_code('G5', 'GST 5%', 5.0, 'GST.OUT', 'GST.IN')
    save_tax_code('H13', 'HST 13% (Ontario)', 13.0, 'GST.OUT', 'GST.IN')
    save_tax_code('H15', 'HST 15% (Atlantic)', 15.0, 'GST.OUT', 'GST.IN')
    save_tax_code('E', 'Exempt (no tax)', 0, '', '')

    return path


# ─── Setup Detailed AR Subledger ─────────────────────────────────
def setup_detailed_ar():
    """Scaffold a Detailed Accounts Receivable subledger report.

    Creates:
      - AR report on the home screen with 3 sample client accounts
      - ARDET total account that accumulates client balances
      - AR.DET total account on the BS that receives the cross-report total
      - Cross-report link: client R. accounts → ARDET → AR.DET → AR.TOT → CA → TA

    Raises ValueError if the AR report already exists or BS report is missing.
    Returns a summary string on success.
    """
    # ── Guard: AR report must not already exist ──
    existing = find_report_by_name('AR')
    if existing:
        raise ValueError("AR report already exists. Cannot create duplicate.")

    # ── Guard: BS report must exist ──
    bs = find_report_by_name('BS')
    if not bs:
        raise ValueError("Balance Sheet (BS) report not found. Create books first.")

    # ── Create accounts ──
    samples = [
        ('R.GREWAY', 'D', 'Gretzky, Wayne'),
        ('R.LEMMAR', 'D', 'Lemieux, Mario'),
        ('R.ORRBOB', 'D', 'Orr, Bobby'),
    ]
    sample_ids = {}
    for name, nb, desc in samples:
        ex = get_account_by_name(name)
        if ex:
            sample_ids[name] = ex['id']
        else:
            sample_ids[name] = add_account(name, nb, desc, 'posting')

    # ARDET — total account on AR report (receives client balances)
    ex = get_account_by_name('ARDET')
    if ex:
        ardet_id = ex['id']
    else:
        ardet_id = add_account('ARDET', 'D', 'Detailed AR - Total', 'total')

    # AR.DET — total account on BS (receives cross-report total from ARDET)
    ex = get_account_by_name('AR.DET')
    if ex:
        ardet_bs_id = ex['id']
    else:
        ardet_bs_id = add_account('AR.DET', 'D', 'Detailed AR', 'total')

    # ── Create the AR report ──
    # Sort after BS(10), IS(20), before AJE(30) — use 25
    ar_report = add_report('AR', 'Accounts Receivable - Detailed', 25)

    # ── Populate AR report items ──
    p = [0]
    def ai(itype, desc='', acct_id=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(ar_report, itype, desc, acct_id, ind, p[0], tt1, sep_style=sep)

    ai('label', 'Accounts Receivable - Detailed')
    ai('label', '')
    ai('label', 'Client Receivables:', ind=1)
    ai('account', '', sample_ids['R.GREWAY'], 2, 'ARDET')
    ai('account', '', sample_ids['R.LEMMAR'], 2, 'ARDET')
    ai('account', '', sample_ids['R.ORRBOB'], 2, 'ARDET')
    ai('separator', sep='single')
    ai('total', '', ardet_id, 3, 'AR.DET')  # cross-report link
    ai('separator', sep='double')

    # ── Insert AR.DET on the BS near existing AR account ──
    bs_items = get_report_items(bs['id'])

    # Find existing AR account on BS
    ar_item = None
    ar_position = None
    ar_total_to = 'CA'  # fallback
    for item in bs_items:
        if item['acct_name'] and item['acct_name'].upper() == 'AR':
            ar_item = item
            ar_position = item['position']
            ar_total_to = item['total_to_1'] or 'AR.TOT'
            break

    if ar_item:
        # Insert AR.DET just after the existing AR account
        insert_pos = ar_position + 1
    else:
        # No AR account found — look for Current Assets total (CA) and insert before it
        for item in bs_items:
            if item['acct_name'] and item['acct_name'].upper() == 'CA':
                insert_pos = item['position'] - 1
                ar_total_to = 'CA'
                break
        else:
            # Last resort: append to end of BS
            insert_pos = None
            ar_total_to = 'CA'

    # AR.DET totals to the same target as AR (typically AR.TOT)
    add_report_item(bs['id'], 'account', '', ardet_bs_id, 2, insert_pos, ar_total_to)

    created = ', '.join(s[0] for s in samples)
    return (f"Detailed AR subledger created. "
            f"Report: AR ({len(samples)} sample clients: {created}). "
            f"Total account ARDET → AR.DET on BS → {ar_total_to}.")


# ─── Setup Detailed AP Subledger ─────────────────────────────────
def setup_detailed_ap():
    """Scaffold a Detailed Accounts Payable subledger report.

    Creates:
      - AP.SUB report on the home screen with 3 sample vendor accounts
      - APDET total account that accumulates vendor balances
      - AP.DET total account on the BS that receives the cross-report total
      - AP.TOT total account on the BS that subtotals AP + AP.CC + AP.DET → CL
      - Cross-report link: vendor P. accounts → APDET → AP.DET → AP.TOT → CL → TL

    Raises ValueError if the AP.SUB report already exists or BS report is missing.
    Returns a summary string on success.
    """
    # ── Guard: AP.SUB report must not already exist ──
    existing = find_report_by_name('AP.SUB')
    if existing:
        raise ValueError("AP.SUB report already exists. Cannot create duplicate.")

    # ── Guard: BS report must exist ──
    bs = find_report_by_name('BS')
    if not bs:
        raise ValueError("Balance Sheet (BS) report not found. Create books first.")

    # ── Create vendor accounts ──
    samples = [
        ('P.BAUEQU', 'C', 'Bauer, Equipment'),
        ('P.CCMSPO', 'C', 'CCM, Sports'),
        ('P.WARHOC', 'C', 'Warrior, Hockey'),
    ]
    sample_ids = {}
    for name, nb, desc in samples:
        ex = get_account_by_name(name)
        if ex:
            sample_ids[name] = ex['id']
        else:
            sample_ids[name] = add_account(name, nb, desc, 'posting')

    # APDET — total account on AP.SUB report (receives vendor balances)
    ex = get_account_by_name('APDET')
    if ex:
        apdet_id = ex['id']
    else:
        apdet_id = add_account('APDET', 'C', 'Detailed AP - Total', 'total')

    # AP.DET — total account on BS (receives cross-report total from APDET)
    ex = get_account_by_name('AP.DET')
    if ex:
        apdet_bs_id = ex['id']
    else:
        apdet_bs_id = add_account('AP.DET', 'C', 'Detailed AP', 'total')

    # AP.TOT — total account on BS (subtotals AP + AP.CC + AP.DET → CL)
    ex = get_account_by_name('AP.TOT')
    if ex:
        aptot_id = ex['id']
    else:
        aptot_id = add_account('AP.TOT', 'C', 'Total Accounts Payable', 'total')

    # ── Create the AP.SUB report ──
    # Sort after AR(25), before AJE(30) — use 26
    ap_report = add_report('AP.SUB', 'Accounts Payable - Detailed', 26)

    # ── Populate AP.SUB report items ──
    p = [0]
    def ai(itype, desc='', acct_id=None, ind=0, tt1='', sep=''):
        p[0] += 10
        add_report_item(ap_report, itype, desc, acct_id, ind, p[0], tt1, sep_style=sep)

    ai('label', 'Accounts Payable - Detailed')
    ai('label', '')
    ai('label', 'Vendor Payables:', ind=1)
    ai('account', '', sample_ids['P.BAUEQU'], 2, 'APDET')
    ai('account', '', sample_ids['P.CCMSPO'], 2, 'APDET')
    ai('account', '', sample_ids['P.WARHOC'], 2, 'APDET')
    ai('separator', sep='single')
    ai('total', '', apdet_id, 3, 'AP.DET')  # cross-report link
    ai('separator', sep='double')

    # ── Restructure BS: add AP.DET and AP.TOT near existing AP accounts ──
    bs_items = get_report_items(bs['id'])

    # Find existing AP accounts on BS and the target they total to
    ap_item = None
    ap_cc_item = None
    ap_total_to = 'CL'  # fallback
    for item in bs_items:
        name = (item['acct_name'] or '').upper()
        if name == 'AP':
            ap_item = item
            ap_total_to = item['total_to_1'] or 'CL'
        elif name == 'AP.CC':
            ap_cc_item = item

    # Re-point existing AP and AP.CC to total to AP.TOT instead of CL
    if ap_item:
        update_report_item(ap_item['id'], total_to_1='AP.TOT')
    if ap_cc_item:
        update_report_item(ap_cc_item['id'], total_to_1='AP.TOT')

    # Determine insertion position — after AP.CC (or after AP if no AP.CC)
    # _resequence() runs after each add_report_item, so re-read positions between inserts.
    def _pos_after(acct_name):
        """Find current position of an account on the BS and return pos+1."""
        for it in get_report_items(bs['id']):
            if (it['acct_name'] or '').upper() == acct_name.upper():
                return it['position'] + 1
        return None

    last_ap = ap_cc_item or ap_item
    last_ap_name = last_ap['acct_name'] if last_ap else ''

    # Insert AP.DET after last AP account
    pos = _pos_after(last_ap_name) if last_ap_name else None
    add_report_item(bs['id'], 'account', '', apdet_bs_id, 2, pos, 'AP.TOT')

    # Insert separator after AP.DET (re-read position since resequence ran)
    pos = _pos_after('AP.DET')
    add_report_item(bs['id'], 'separator', '', None, 0, pos, sep_style='single')

    # Insert AP.TOT after the separator — find AP.DET pos, skip 2 (AP.DET + sep)
    items_now = get_report_items(bs['id'])
    for i, it in enumerate(items_now):
        if (it['acct_name'] or '').upper() == 'AP.DET':
            # AP.DET is at index i, separator is i+1, insert AP.TOT at i+2
            pos = items_now[i + 1]['position'] + 1 if i + 1 < len(items_now) else None
            break
    else:
        pos = None
    add_report_item(bs['id'], 'total', '', aptot_id, 3, pos, ap_total_to)

    created = ', '.join(s[0] for s in samples)
    return (f"Detailed AP subledger created. "
            f"Report: AP.SUB ({len(samples)} sample vendors: {created}). "
            f"Total account APDET → AP.DET on BS → AP.TOT → {ap_total_to}.")


# ─── CaseWare AJE Import ────────────────────────────────────────

def parse_csw_aje(file_path):
    """Parse CaseWare AJE export (IIF or Venice format).

    Auto-detects format from file content.
    Returns:
      {
        'format': 'iif' | 'venice',
        'entries': [
          {
            'num': '01',
            'date': '2024-12-01',
            'description': '...',
            'lines': [
              {'csw_account': 'Dividends paid-taxable', 'csw_number': '', 'amount_cents': 10000},
              ...
            ]
          }, ...
        ],
        'csw_accounts': [
          {'name': 'Dividends paid-taxable', 'number': ''}, ...
        ]
      }
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        raw = f.read()

    if '!TRNS' in raw or 'ENDTRNS' in raw:
        return _parse_iif_aje(raw)
    elif 'STOP' in raw:
        return _parse_venice_aje(raw)
    else:
        raise ValueError("Unrecognized file format. Expected IIF (TRNS/ENDTRNS) or Venice (STOP delimited).")


def _parse_iif_aje(raw):
    """Parse QuickBooks IIF format AJE export."""
    import re
    lines = raw.split('\n')
    entries = []
    current_lines = []
    seen_accounts = {}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('!'):
            continue
        cols = stripped.split('\t')
        marker = cols[0].strip().upper() if cols else ''

        if marker == 'TRNS' or marker == 'SPL':
            # Col indices: 0=marker, 1=ID, 2=TYPE, 3=DATE, 4=ACCNT, 5=NAME, 6=CLASS, 7=AMOUNT, 8=DOCNUM, 9=MEMO
            acct_name = cols[4].strip() if len(cols) > 4 else ''
            amount_str = cols[7].strip() if len(cols) > 7 else '0'
            docnum = cols[8].strip() if len(cols) > 8 else ''
            memo = cols[9].strip() if len(cols) > 9 else ''
            date_str = cols[3].strip() if len(cols) > 3 else ''

            amount_cents = parse_amount(amount_str)

            current_lines.append({
                'csw_account': acct_name,
                'csw_number': '',
                'amount_cents': amount_cents,
                'date': date_str,
                'docnum': docnum,
                'memo': memo,
                'is_trns': marker == 'TRNS',
            })

            if acct_name and acct_name not in seen_accounts:
                seen_accounts[acct_name] = {'name': acct_name, 'number': ''}

        elif marker == 'ENDTRNS':
            if current_lines:
                # Extract entry info from the TRNS line
                trns = current_lines[0]
                # Parse AJE number from DOCNUM (e.g. "AJE01" -> "01")
                num_match = re.search(r'AJE\s*(\d+)', trns['docnum'], re.IGNORECASE)
                aje_num = num_match.group(1) if num_match else trns['docnum']

                # Normalize date (IIF uses M/D/YY or M/D/YYYY)
                entry_date = normalize_date(trns['date'])
                if not entry_date:
                    entry_date = trns['date']

                entries.append({
                    'num': aje_num,
                    'date': entry_date,
                    'description': trns['memo'],
                    'lines': [{'csw_account': l['csw_account'],
                               'csw_number': l['csw_number'],
                               'amount_cents': l['amount_cents']}
                              for l in current_lines],
                })
            current_lines = []

    return {
        'format': 'iif',
        'entries': entries,
        'csw_accounts': list(seen_accounts.values()),
    }


def _parse_venice_aje(raw):
    """Parse Venice/MYOB format AJE export."""
    import re
    blocks = raw.split('STOP')
    entries = []
    seen_accounts = {}

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        if not lines:
            continue

        # Header line: chars 0-10 = date (DD/MM/YYYY), chars 10-15 = ref (AJEnn), rest = description
        header = lines[0]
        if len(header) < 15:
            continue

        date_str = header[0:10].strip()
        ref_str = header[10:15].strip()
        description = header[15:].strip()

        # Parse date explicitly as DD/MM/YYYY (Venice format)
        try:
            entry_date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            entry_date = normalize_date(date_str) or date_str

        # Parse AJE number
        num_match = re.search(r'AJE\s*(\d+)', ref_str, re.IGNORECASE)
        aje_num = num_match.group(1) if num_match else ref_str

        # Detail lines: account name, account number, amount
        entry_lines = []
        for dline in lines[1:]:
            dline = dline.rstrip()
            if not dline.strip():
                continue
            # Pattern: account name (with spaces), then 2+ spaces, then 4-digit number, then spaces, then signed amount
            m = re.match(r'^(.+?)\s{2,}(\d{4})\s+([-\d,.]+)\s*$', dline)
            if m:
                acct_name = m.group(1).strip()
                acct_num = m.group(2).strip()
                amount_cents = parse_amount(m.group(3))

                entry_lines.append({
                    'csw_account': acct_name,
                    'csw_number': acct_num,
                    'amount_cents': amount_cents,
                })

                if acct_name not in seen_accounts:
                    seen_accounts[acct_name] = {'name': acct_name, 'number': acct_num}

        if entry_lines:
            entries.append({
                'num': aje_num,
                'date': entry_date,
                'description': description,
                'lines': entry_lines,
            })

    return {
        'format': 'venice',
        'entries': entries,
        'csw_accounts': list(seen_accounts.values()),
    }


def auto_match_accounts(csw_accounts):
    """Try to match CsW account names to Grid accounts.

    Match strategies (in order):
      1. Exact name match (case-insensitive)
      2. Grid account description contains CsW name (case-insensitive)
      3. CsW number matches Grid account_number field
      4. None — user must assign

    Args:
        csw_accounts: list of {'name': str, 'number': str}

    Returns:
        dict: {csw_name: {'id': int, 'name': str} or None}
    """
    all_accounts = get_accounts()
    suggestions = {}

    for csw in csw_accounts:
        csw_name = csw['name']
        csw_num = csw.get('number', '')
        match = None

        # Strategy 1: exact name match
        for a in all_accounts:
            if a['name'].lower() == csw_name.lower():
                match = {'id': a['id'], 'name': a['name']}
                break

        # Strategy 2: Grid description contains CsW name
        if not match:
            csw_lower = csw_name.lower()
            for a in all_accounts:
                if csw_lower in (a['description'] or '').lower():
                    match = {'id': a['id'], 'name': a['name']}
                    break

        # Strategy 3: CsW number matches Grid account_number
        if not match and csw_num:
            for a in all_accounts:
                if a['account_number'] and a['account_number'] == csw_num:
                    match = {'id': a['id'], 'name': a['name']}
                    break

        suggestions[csw_name] = match

    return suggestions


def import_aje_entries(entries, account_map, ref_prefix):
    """Post parsed AJE entries as transactions.

    Args:
        entries: list from parse_csw_aje()['entries']
        account_map: {csw_account_name: grid_account_id}
        ref_prefix: e.g. '25AJE'

    Returns:
        dict: {posted: int, skipped: int, errors: list}
    """
    posted = 0
    skipped = 0
    errors = []

    for i, entry in enumerate(entries):
        ref = f"{ref_prefix}{entry['num']}"
        entry_date = entry['date']
        desc = entry['description']

        # Build transaction lines
        txn_lines = []
        unmapped = False
        for line in entry['lines']:
            grid_acct_id = account_map.get(line['csw_account'])
            if not grid_acct_id:
                errors.append({'entry': ref, 'reason': f"Unmapped account: {line['csw_account']}"})
                unmapped = True
                break
            txn_lines.append((grid_acct_id, line['amount_cents'], desc))

        if unmapped:
            skipped += 1
            continue

        # Validate balance
        total = sum(l[1] for l in txn_lines)
        if total != 0:
            errors.append({'entry': ref, 'reason': f"Entry does not balance: off by {total/100:.2f}"})
            skipped += 1
            continue

        try:
            add_transaction(entry_date, ref, desc, txn_lines)
            posted += 1
        except ValueError as e:
            errors.append({'entry': ref, 'reason': str(e)})
            skipped += 1

    return {'posted': posted, 'skipped': skipped, 'errors': errors}
