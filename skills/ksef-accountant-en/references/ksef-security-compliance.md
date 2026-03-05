# Security & Compliance for KSeF

Security requirements, compliance and best practices.

**SECURITY WARNING:**
All code examples in this document are **educational and conceptual** — architectural patterns for the user to implement in their own system. This skill does NOT implement these mechanisms, does NOT store tokens, does NOT connect to Vault and does NOT manage encryption keys.

**Environment variables** mentioned in this document (e.g., `KSEF_TOKEN`, `KSEF_ENCRYPTION_KEY`) are declared in the skill metadata as optional. The skill does not implicitly request them — if the user provides them, the agent can use them in suggested code. All variables are described in the `env` section of the SKILL.md file.

**NEVER paste tokens, encryption keys, certificates or other credentials directly in the conversation with the agent.** Use only:
- Platform environment variables (env vars)
- Secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager)
- Ephemeral session variables (ephemeral env vars)

Before using patterns in a production environment:
1. Conduct a security review
2. Use dedicated, tested tools instead of custom implementations
3. Never run unverified code from external sources
4. Implement principle of least privilege
5. Regularly update dependencies and conduct security audits
6. Test exclusively on the DEMO environment (`https://ksef-demo.mf.gov.pl`) — never on production

---

## Platform vs. Skill Guarantees — Pre-installation Verification

This skill declares security flags in **two sources**:
- **SKILL.md frontmatter** — contains `disableModelInvocation: true` (camelCase) and `disable-model-invocation: true` (kebab-case), as well as env var declarations with `secret: true` for variables containing credentials.
- **Manifest [`skill.json`](../skill.json)** — a dedicated machine-readable file with full security metadata, env var declarations (with `secret` and `scope` fields) and constraints. It is the source of truth for registries and scanners that may not parse YAML frontmatter.

However, **both of these sources are skill declarations, not platform guarantees**. Enforcement of these flags depends solely on the hosting platform.

**Known issue:** Registry metadata displayed by the platform may not reflect values from the frontmatter or `skill.json`. If the platform shows `disable-model-invocation: not set` (or omits this flag), or does not display environment variables as registered — the protection **is not active**, regardless of what the skill files declare.

**Mandatory pre-installation verification:**

1. **Compare registry metadata with frontmatter and `skill.json`** — after adding the skill to the platform, open the registry metadata view. Verify that:
   - `disable-model-invocation` = `true`
   - Environment variables `KSEF_TOKEN` and `KSEF_ENCRYPTION_KEY` are visible as registered secrets
   - Other platform-level security flags (if any) are correctly set
   - If ANY field does not match frontmatter/`skill.json` — treat the skill as higher risk
2. **Confirm environment variable isolation** — variables (`KSEF_TOKEN`, `KSEF_ENCRYPTION_KEY`, `KSEF_BASE_URL`) must not be logged, displayed in conversation or accessible to other skills
3. **If the platform does NOT enforce the `disableModelInvocation` flag:**
   - DO NOT configure any environment variables with credentials
   - DO NOT provide tokens, certificates or encryption keys
   - DO NOT allow autonomous use of the skill
   - Use only in manual mode (explicit user action) and only with the DEMO environment (`https://ksef-demo.mf.gov.pl`)
4. **Report discrepancy** — if registry metadata does not match frontmatter/`skill.json`, report it to the platform provider as a security issue requiring a fix. Provide the `skill.json` filename as an alternative metadata source if the platform does not parse YAML frontmatter

---

## VAT White List

### Automatic Verification

```python
import requests
from datetime import datetime

def verify_contractor_white_list(nip, bank_account, date=None):
    """
    Checks the contractor on the VAT White List
    API: https://wl-api.mf.gov.pl/
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {
            'valid': False,
            'reason': f'API error: {e}',
            'risk': 'UNKNOWN'
        }

    # Check VAT status
    subject = data['result']['subject']

    if subject['statusVat'] != 'Czynny':
        return {
            'valid': False,
            'reason': f"Contractor VAT status: {subject['statusVat']}",
            'risk': 'HIGH',
            'details': subject
        }

    # Check bank account
    accounts = subject.get('accountNumbers', [])

    # Normalize account number (remove spaces)
    bank_account_normalized = bank_account.replace(' ', '')

    for acc in accounts:
        if acc.replace(' ', '') == bank_account_normalized:
            return {
                'valid': True,
                'name': subject['name'],
                'status': subject['statusVat'],
                'verified_account': acc
            }

    # Account not on the list
    return {
        'valid': False,
        'reason': 'Bank account is not on the White List',
        'risk': 'HIGH',
        'valid_accounts': accounts,
        'details': subject
    }
```

### Integration with Payments

```python
def before_payment_check(invoice, payment):
    """
    Verification before executing a transfer
    """
    # 1. Check White List
    verification = verify_contractor_white_list(
        nip=invoice.seller_nip,
        bank_account=payment.to_account,
        date=payment.date.strftime('%Y-%m-%d')
    )

    if not verification['valid']:
        # Hold payment
        payment.status = 'HOLD'
        payment.hold_reason = verification['reason']

        # Send alert
        send_critical_alert(
            level='HIGH',
            title='Payment held - VAT White List',
            message=f"Contractor: {invoice.seller_name} ({invoice.seller_nip})\n"
                   f"Amount: {payment.amount} PLN\n"
                   f"Reason: {verification['reason']}\n"
                   f"Invoice: {invoice.number}",
            invoice=invoice,
            payment=payment
        )

        return False

    # 2. Check if MPP is required
    if invoice.total_gross > 15000 and invoice.has_attachment_15_goods:
        if payment.type != 'MPP':
            send_warning_alert(
                title='Invoice requires MPP',
                message=f"Invoice {invoice.number} requires the split payment mechanism"
            )
            return False

    return True
```

---

## Token Security

### Token Storage

```python
from cryptography.fernet import Fernet
import os

class SecureTokenStorage:
    """
    Encrypted KSeF token storage
    """
    def __init__(self, encryption_key=None):
        if encryption_key is None:
            # Read from environment variable
            encryption_key = os.environ.get('KSEF_ENCRYPTION_KEY')

        if encryption_key is None:
            raise ValueError("Missing encryption key")

        self.cipher = Fernet(encryption_key.encode())

    def store_token(self, token_name, token_value):
        """Store token (encrypted)"""
        encrypted = self.cipher.encrypt(token_value.encode())
        # Save to database or vault
        db.tokens.insert({
            'name': token_name,
            'value': encrypted,
            'created_at': datetime.now()
        })

    def retrieve_token(self, token_name):
        """Retrieve token (decrypt)"""
        record = db.tokens.find_one({'name': token_name})
        if not record:
            raise ValueError(f"Token {token_name} does not exist")

        decrypted = self.cipher.decrypt(record['value'])
        return decrypted.decode()

    def rotate_token(self, token_name, new_token_value):
        """Token rotation (best practice: every 90 days)"""
        # Archive old token
        old_record = db.tokens.find_one({'name': token_name})
        db.tokens_archive.insert({
            **old_record,
            'archived_at': datetime.now()
        })

        # Store new one
        self.store_token(token_name, new_token_value)
```

### Integration with Vault (HashiCorp)

```python
import hvac

class VaultTokenStorage:
    """
    Storage in HashiCorp Vault (production)
    """
    def __init__(self, vault_url, vault_token):
        self.client = hvac.Client(url=vault_url, token=vault_token)

    def store_token(self, token_name, token_value):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f'ksef/tokens/{token_name}',
            secret={'value': token_value}
        )

    def retrieve_token(self, token_name):
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=f'ksef/tokens/{token_name}'
        )
        return secret['data']['data']['value']
```

---

## Audit Trail

### Operation Logging

```python
import logging
from datetime import datetime

class AuditLogger:
    """
    Immutable audit log (append-only)
    """
    def __init__(self):
        self.logger = logging.getLogger('ksef_audit')

    def log_operation(self, operation_type, user, entity_type, entity_id, details=None):
        """
        Every operation MUST be logged
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation_type,  # CREATE, READ, UPDATE, DELETE
            'user': user,
            'entity_type': entity_type,  # INVOICE, PAYMENT, etc.
            'entity_id': entity_id,
            'details': details or {},
            'ip_address': self._get_client_ip(),
            'user_agent': self._get_user_agent(),
            'session_id': self._get_session_id()
        }

        # Save to immutable storage (append-only)
        audit_db.insert(audit_entry)

        # Log to file (for compliance)
        self.logger.info(json.dumps(audit_entry))

    def log_ai_decision(self, invoice, prediction, action):
        """
        Special logging for AI decisions
        """
        self.log_operation(
            operation_type='AI_CLASSIFICATION',
            user='AI_SYSTEM',
            entity_type='INVOICE',
            entity_id=invoice.id,
            details={
                'model_name': 'ExpenseClassifier',
                'model_version': '2.1',
                'prediction': prediction['category'],
                'confidence': prediction['confidence'],
                'action_taken': action,
                'reviewed_by_human': action == 'MANUAL_REVIEW'
            }
        )
```

### Audit Review

```python
def audit_report(start_date, end_date, user=None):
    """
    Generate audit report
    """
    query = {
        'timestamp': {
            '$gte': start_date.isoformat(),
            '$lte': end_date.isoformat()
        }
    }

    if user:
        query['user'] = user

    entries = audit_db.find(query).sort('timestamp', 1)

    report = {
        'period': f"{start_date} - {end_date}",
        'total_operations': 0,
        'by_type': {},
        'by_user': {},
        'entries': []
    }

    for entry in entries:
        report['total_operations'] += 1
        report['by_type'][entry['operation']] = \
            report['by_type'].get(entry['operation'], 0) + 1
        report['by_user'][entry['user']] = \
            report['by_user'].get(entry['user'], 0) + 1
        report['entries'].append(entry)

    return report
```

---

## Backup and Disaster Recovery

### 3-2-1 Strategy

**Business requirements:** Accounting data must be protected with redundant backups following the 3-2-1 rule:
- **3 copies** of data (production + 2 backups)
- **2 different media types** (e.g., local SSD + external storage)
- **1 copy offsite** (cloud or remote location)

**Implementation approach:**
1. Use built-in backup solutions from your database provider (managed backups, automated snapshots)
2. Schedule daily automatic backups during low-activity hours
3. Store backups in multiple locations (local fast storage + remote cloud)
4. Implement automatic backup verification for data integrity assurance
5. Retain backups per legal requirements (minimum 10 years for accounting data)
6. Document and regularly test disaster recovery procedures

**For production systems:**
- Leverage managed database services (AWS RDS, Azure Database, Google Cloud SQL) with automatic backup features
- Use enterprise backup solutions designed for accounting/financial data
- Implement monitoring and alerting for backup failures
- Ensure backup processes do not disrupt accounting operations

### KSeF Synchronization for Disaster Recovery

**Key principle:** KSeF is the source of truth for all invoices. If local data is lost, it can be reconstructed from KSeF.

**Recovery process:**
1. **Restore from backup** - Use your infrastructure provider's restore procedures
2. **Synchronize with KSeF** - Download invoices from KSeF API for the last 7-30 days (depending on backup age)
3. **Verify data integrity** - Compare local invoice records with KSeF to identify discrepancies
4. **Reconcile differences** - Update local database with authoritative KSeF data
5. **Notify stakeholders** - Inform accounting team when recovery is complete and system is operational

**Important:** Test disaster recovery procedures quarterly to ensure they work when needed.

---

## GDPR

### Personal Data in Invoices

```python
def anonymize_invoice_for_archive(invoice, retention_years=10):
    """
    Anonymization after retention period expires
    """
    retention_date = invoice.issue_date + timedelta(days=365 * retention_years)

    if datetime.now() > retention_date:
        # Data to anonymize (GDPR)
        invoice.buyer_name = "***ANONYMIZED***"
        invoice.buyer_address = "***"
        invoice.buyer_email = None
        invoice.buyer_phone = None

        # Keep NIP (required for fiscal purposes)
        # invoice.buyer_nip - KEEP

        invoice.anonymized_at = datetime.now()
        invoice.save()
```

### Data Deletion Request (Right to be Forgotten)

```python
def handle_gdpr_deletion_request(contractor_nip):
    """
    WARNING: Invoices are subject to mandatory retention (5-10 years)
    They cannot be deleted during the retention period!
    """
    # 1. Check if retention period has passed
    invoices = get_all_invoices_for_contractor(contractor_nip)

    for invoice in invoices:
        retention_date = invoice.issue_date + timedelta(days=365 * 10)

        if datetime.now() < retention_date:
            return {
                'status': 'REJECTED',
                'reason': 'Invoices are subject to mandatory retention',
                'retention_until': retention_date
            }

    # 2. If period has passed - anonymize
    for invoice in invoices:
        anonymize_invoice_for_archive(invoice)

    return {
        'status': 'COMPLETED',
        'anonymized_invoices': len(invoices)
    }
```

---

## Access Control (RBAC)

### Roles and Permissions

```python
ROLES = {
    'ADMIN': [
        'invoice.create', 'invoice.read', 'invoice.update', 'invoice.delete',
        'payment.create', 'payment.read', 'payment.update', 'payment.delete',
        'user.manage', 'settings.manage'
    ],
    'ACCOUNTANT': [
        'invoice.create', 'invoice.read', 'invoice.update',
        'payment.create', 'payment.read', 'payment.update',
        'report.generate'
    ],
    'VIEWER': [
        'invoice.read', 'payment.read', 'report.view'
    ]
}

def check_permission(user, permission):
    """
    Check if user has permission
    """
    user_role = user.role
    allowed_permissions = ROLES.get(user_role, [])

    if permission not in allowed_permissions:
        audit_logger.log_operation(
            operation_type='PERMISSION_DENIED',
            user=user.username,
            entity_type='PERMISSION',
            entity_id=permission
        )
        raise PermissionError(f"User {user.username} does not have permission: {permission}")

    return True
```

---

## SSL/TLS Certificates

### Connections to KSeF

```python
import ssl
import certifi

def secure_ksef_connection():
    """
    Always use HTTPS with certificate verification
    """
    session = requests.Session()

    # 1. Verify certificate (NEVER verify=False)
    session.verify = certifi.where()

    # 2. Use strong cipher suites
    session.mount('https://', requests.adapters.HTTPAdapter(
        max_retries=3,
        pool_connections=10,
        pool_maxsize=20
    ))

    # 3. Set timeout
    session.request = lambda *args, **kwargs: \
        requests.Session.request(session, *args, timeout=30, **kwargs)

    return session
```

---

## Secure Development Practices

### 1. Avoid Dynamic Code Execution

**NEVER use:**
- `eval()` or `exec()` on user input or external data
- Shell command execution with string concatenation
- Dynamic SQL queries built through string concatenation

**INSTEAD use:**
- Parameterized database queries (prevents SQL injection)
- Validated, type-checked input data
- Structured API calls with proper argument handling
- Built-in libraries and frameworks designed for accounting operations

### 2. Input Validation

```python
def validate_invoice_number(number):
    """Validate before using in queries"""
    # Only alphanumeric, hyphens, slashes
    import re
    if not re.match(r'^[A-Z0-9/-]+$', number):
        raise ValueError("Invalid invoice number")
    if len(number) > 50:
        raise ValueError("Invoice number too long")
    return number
```

### 3. Principle of Least Privilege

```python
# Database user with minimum permissions
DB_CONFIG = {
    'user': 'ksef_readonly',  # SELECT only for reports
    'user': 'ksef_app',       # SELECT + INSERT + UPDATE for app
    'user': 'ksef_admin',     # All permissions (admin only)
}
```

### 4. Use Enterprise-Grade Solutions

For production accounting systems:
- **Databases:** Managed database services with automatic backups and point-in-time recovery
- **Monitoring:** Professional monitoring platforms with alerting capabilities
- **Security:** Enterprise identity management and access control systems
- **Compliance:** Audit logging solutions designed for financial data

---

## Security Checklist

- [ ] KSeF tokens encrypted (Fernet/Vault)
- [ ] VAT White List checked before every payment
- [ ] Audit trail of all operations
- [ ] 3-2-1 backup (daily)
- [ ] HTTPS with certificate verification
- [ ] RBAC (access control)
- [ ] Retention policy compliant with law (10 years)
- [ ] GDPR - anonymization after retention period
- [ ] Monitoring and alerts
- [ ] Disaster recovery plan (tested quarterly)

---

**Compliance:** Implementing the above practices supports compliance with:
- VAT Act
- GDPR
- Accounting Act
- ISO 27001 standards (optional)
