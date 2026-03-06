# Security & Compliance dla KSeF

Wymagania bezpieczeństwa, zgodności i najlepsze praktyki.

**⚠️ OSTRZEŻENIE BEZPIECZEŃSTWA:**
Wszystkie przykłady kodu w tym dokumencie mają charakter **edukacyjny i koncepcyjny** — to wzorce architektoniczne do implementacji przez użytkownika w jego własnym systemie. Ten skill NIE implementuje tych mechanizmów, NIE przechowuje tokenów, NIE łączy się z Vault i NIE zarządza kluczami szyfrowania.

**Zmienne środowiskowe** wymienione w tym dokumencie (np. `KSEF_TOKEN`, `KSEF_ENCRYPTION_KEY`) są zadeklarowane w metadanych skilla jako opcjonalne. Skill nie prosi o nie niejawnie — jeśli użytkownik je udostępni, agent może je wykorzystać w sugerowanym kodzie. Wszystkie zmienne są opisane w sekcji `env` pliku SKILL.md.

**NIGDY nie wklejaj tokenów, kluczy szyfrowania, certyfikatów ani innych danych uwierzytelniających bezpośrednio w rozmowie z agentem.** Używaj wyłącznie:
- Zmiennych środowiskowych platformy (env vars)
- Menedżera sekretów (np. HashiCorp Vault, AWS Secrets Manager)
- Tymczasowych zmiennych sesji (ephemeral env vars)

Przed użyciem wzorców w środowisku produkcyjnym:
1. Przeprowadź security review
2. Użyj dedykowanych, przetestowanych narzędzi zamiast własnych implementacji
3. Nigdy nie uruchamiaj niezweryfikowanego kodu z zewnętrznych źródeł
4. Implementuj principle of least privilege
5. Regularnie aktualizuj zależności i przeprowadzaj audyty bezpieczeństwa
6. Testuj wyłącznie na środowisku DEMO (`https://ksef-demo.mf.gov.pl`) — nigdy na produkcji

---

## Gwarancje platformy vs. skilla — weryfikacja przed instalacją

Ten skill deklaruje flagi bezpieczeństwa w **dwóch źródłach**:
- **Frontmatter SKILL.md** — zawiera `disableModelInvocation: true` (camelCase) oraz `disable-model-invocation: true` (kebab-case), a także deklaracje env vars z `secret: true` dla zmiennych zawierających dane uwierzytelniające.
- **Manifest [`skill.json`](../skill.json)** — dedykowany plik maszynowo czytelny z pełnymi metadanymi bezpieczeństwa, deklaracjami env vars (z polem `secret` i `scope`) oraz ograniczeniami. Jest źródłem prawdy dla rejestrów i skanerów, które mogą nie parsować frontmatter YAML.

Jednak **oba te źródła to deklaracje skilla, nie gwarancje platformy**. Wymuszanie tych flag zależy wyłącznie od platformy hostingowej.

**Znany problem:** Metadane rejestru (registry metadata) wyświetlane przez platformę mogą nie odzwierciedlać wartości z frontmatter ani z `skill.json`. Jeśli platforma pokazuje `disable-model-invocation: not set` (lub pomija tę flagę), albo nie wyświetla zmiennych środowiskowych jako zarejestrowanych — ochrona **nie jest aktywna**, niezależnie od tego, co deklarują pliki skilla.

**Obowiązkowa weryfikacja przed instalacją:**

1. **Porównaj metadane rejestru z frontmatter i `skill.json`** — po dodaniu skilla do platformy, otwórz widok metadanych rejestru. Zweryfikuj, że:
   - `disable-model-invocation` = `true`
   - Zmienne środowiskowe `KSEF_TOKEN` i `KSEF_ENCRYPTION_KEY` są widoczne jako zarejestrowane sekrety
   - Inne flagi bezpieczeństwa na poziomie platformy (jeśli istnieją) są poprawnie ustawione
   - Jeśli JAKIEKOLWIEK pole nie zgadza się z frontmatter/`skill.json` — traktuj skill jako wyższego ryzyka
2. **Potwierdź izolację zmiennych środowiskowych** — zmienne (`KSEF_TOKEN`, `KSEF_ENCRYPTION_KEY`, `KSEF_BASE_URL`) nie mogą być logowane, wyświetlane w konwersacji ani dostępne dla innych skilli
3. **Jeśli platforma NIE wymusza flagi `disableModelInvocation`:**
   - NIE konfiguruj żadnych zmiennych środowiskowych z danymi uwierzytelniającymi
   - NIE udostępniaj tokenów, certyfikatów ani kluczy szyfrowania
   - NIE zezwalaj na autonomiczne użycie skilla
   - Używaj wyłącznie w trybie ręcznym (jawna akcja użytkownika) i tylko ze środowiskiem DEMO (`https://ksef-demo.mf.gov.pl`)
4. **Zgłoś rozbieżność** — jeśli metadane rejestru nie pasują do frontmatter/`skill.json`, zgłoś to dostawcy platformy jako problem bezpieczeństwa wymagający naprawy. Podaj nazwę pliku `skill.json` jako alternatywne źródło metadanych, jeśli platforma nie parsuje frontmatter YAML

---

## Biała Lista VAT

### Automatyczna Weryfikacja

```python
import requests
from datetime import datetime

def verify_contractor_white_list(nip, bank_account, date=None):
    """
    Sprawdza kontrahenta na białej liście VAT
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
            'reason': f'Błąd API: {e}',
            'risk': 'UNKNOWN'
        }

    # Sprawdź status VAT
    subject = data['result']['subject']

    if subject['statusVat'] != 'Czynny':
        return {
            'valid': False,
            'reason': f"Kontrahent VAT: {subject['statusVat']}",
            'risk': 'HIGH',
            'details': subject
        }

    # Sprawdź konto bankowe
    accounts = subject.get('accountNumbers', [])

    # Normalizuj numer konta (usuń spacje)
    bank_account_normalized = bank_account.replace(' ', '')

    for acc in accounts:
        if acc.replace(' ', '') == bank_account_normalized:
            return {
                'valid': True,
                'name': subject['name'],
                'status': subject['statusVat'],
                'verified_account': acc
            }

    # Konto nie na liście
    return {
        'valid': False,
        'reason': 'Konto bankowe nie znajduje się na białej liście',
        'risk': 'HIGH',
        'valid_accounts': accounts,
        'details': subject
    }
```

### Integracja z Płatnościami

```python
def before_payment_check(invoice, payment):
    """
    Weryfikacja przed wykonaniem przelewu
    """
    # 1. Sprawdź białą listę
    verification = verify_contractor_white_list(
        nip=invoice.seller_nip,
        bank_account=payment.to_account,
        date=payment.date.strftime('%Y-%m-%d')
    )

    if not verification['valid']:
        # Wstrzymaj płatność
        payment.status = 'HOLD'
        payment.hold_reason = verification['reason']

        # Wysłij alert
        send_critical_alert(
            level='HIGH',
            title='Płatność wstrzymana - Biała lista VAT',
            message=f"Kontrahent: {invoice.seller_name} ({invoice.seller_nip})\n"
                   f"Kwota: {payment.amount} PLN\n"
                   f"Powód: {verification['reason']}\n"
                   f"Faktura: {invoice.number}",
            invoice=invoice,
            payment=payment
        )

        return False

    # 2. Sprawdź czy wymaga MPP
    if invoice.total_gross > 15000 and invoice.has_attachment_15_goods:
        if payment.type != 'MPP':
            send_warning_alert(
                title='Faktura wymaga MPP',
                message=f"Faktura {invoice.number} wymaga mechanizmu podzielonej płatności"
            )
            return False

    return True
```

---

## Bezpieczeństwo Tokenów

### Przechowywanie Tokenów

```python
from cryptography.fernet import Fernet
import os

class SecureTokenStorage:
    """
    Szyfrowane przechowywanie tokenów KSeF
    """
    def __init__(self, encryption_key=None):
        if encryption_key is None:
            # Wczytaj z environment variable
            encryption_key = os.environ.get('KSEF_ENCRYPTION_KEY')

        if encryption_key is None:
            raise ValueError("Brak klucza szyfrowania")

        self.cipher = Fernet(encryption_key.encode())

    def store_token(self, token_name, token_value):
        """Zapisz token (zaszyfrowany)"""
        encrypted = self.cipher.encrypt(token_value.encode())
        # Zapisz do bazy lub vault
        db.tokens.insert({
            'name': token_name,
            'value': encrypted,
            'created_at': datetime.now()
        })

    def retrieve_token(self, token_name):
        """Pobierz token (odszyfruj)"""
        record = db.tokens.find_one({'name': token_name})
        if not record:
            raise ValueError(f"Token {token_name} nie istnieje")

        decrypted = self.cipher.decrypt(record['value'])
        return decrypted.decode()

    def rotate_token(self, token_name, new_token_value):
        """Rotacja tokena (best practice: co 90 dni)"""
        # Archiwizuj stary token
        old_record = db.tokens.find_one({'name': token_name})
        db.tokens_archive.insert({
            **old_record,
            'archived_at': datetime.now()
        })

        # Zapisz nowy
        self.store_token(token_name, new_token_value)
```

### Integracja z Vault (HashiCorp)

```python
import hvac

class VaultTokenStorage:
    """
    Przechowywanie w HashiCorp Vault (produkcja)
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

### Logowanie Operacji

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
        Każda operacja MUSI być zalogowana
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

        # Zapisz do immutable storage (append-only)
        audit_db.insert(audit_entry)

        # Log do pliku (dla compliance)
        self.logger.info(json.dumps(audit_entry))

    def log_ai_decision(self, invoice, prediction, action):
        """
        Specjalne logowanie decyzji AI
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

### Przegląd Audytu

```python
def audit_report(start_date, end_date, user=None):
    """
    Generuj raport audytowy
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

## Backup i Disaster Recovery

### Strategia 3-2-1

**Wymagania biznesowe:** Dane księgowe muszą być chronione za pomocą redundantnych kopii zapasowych według zasady 3-2-1:
- **3 kopie** danych (produkcja + 2 backupy)
- **2 różne typy nośników** (np. lokalny SSD + zewnętrzny storage)
- **1 kopia poza siedzibą** (chmura lub zdalna lokalizacja)

**Podejście implementacyjne:**
1. Używaj wbudowanych rozwiązań backup dostawcy bazy danych (managed backups, automated snapshots)
2. Zaplanuj codzienne automatyczne backupy w godzinach niskiej aktywności
3. Przechowuj backupy w wielu lokalizacjach (lokalny szybki storage + zdalna chmura)
4. Zaimplementuj automatyczną weryfikację backupów dla zapewnienia integralności danych
5. Zachowuj backupy zgodnie z wymogami prawnymi (minimum 10 lat dla danych księgowych)
6. Dokumentuj i regularnie testuj procedury disaster recovery

**Dla systemów produkcyjnych:**
- Wykorzystuj zarządzane usługi baz danych (AWS RDS, Azure Database, Google Cloud SQL) z funkcjami automatycznego backupu
- Używaj rozwiązań enterprise backup zaprojektowanych dla danych księgowych/finansowych
- Zaimplementuj monitoring i alerty dla niepowodzeń backupu
- Upewnij się, że procesy backup nie zakłócają operacji księgowych

### Synchronizacja z KSeF dla Disaster Recovery

**Kluczowa zasada:** KSeF jest źródłem prawdy dla wszystkich faktur. Jeśli lokalne dane zostaną utracone, mogą być zrekonstruowane z KSeF.

**Proces odzyskiwania:**
1. **Przywróć z backupu** - Użyj procedur restore dostawcy infrastruktury
2. **Synchronizuj z KSeF** - Pobierz faktury z KSeF API z ostatnich 7-30 dni (w zależności od wieku backupu)
3. **Weryfikuj integralność danych** - Porównaj lokalne zapisy faktur z KSeF aby zidentyfikować rozbieżności
4. **Uzgodnij różnice** - Zaktualizuj lokalną bazę danych autorytatywnymi danymi z KSeF
5. **Powiadom zainteresowanych** - Poinformuj zespół księgowy gdy odzyskiwanie jest zakończone i system działa

**Ważne:** Testuj procedury disaster recovery kwartalnie aby upewnić się, że działają gdy są potrzebne.

---

## RODO / GDPR

### Dane Osobowe w Fakturach

```python
def anonymize_invoice_for_archive(invoice, retention_years=10):
    """
    Anonimizacja po upływie okresu przechowywania
    """
    retention_date = invoice.issue_date + timedelta(days=365 * retention_years)

    if datetime.now() > retention_date:
        # Dane do anonimizacji (RODO)
        invoice.buyer_name = "***ANONIMIZOWANE***"
        invoice.buyer_address = "***"
        invoice.buyer_email = None
        invoice.buyer_phone = None

        # Zachowaj NIP (wymagane fiscalnie)
        # invoice.buyer_nip - POZOSTAW

        invoice.anonymized_at = datetime.now()
        invoice.save()
```

### Żądanie Usunięcia Danych (Right to be Forgotten)

```python
def handle_gdpr_deletion_request(contractor_nip):
    """
    ⚠️ UWAGA: Faktury podlegają obowiązkowi przechowywania (5-10 lat)
    Nie można ich usunąć w okresie przechowywania!
    """
    # 1. Sprawdź czy okres przechowywania minął
    invoices = get_all_invoices_for_contractor(contractor_nip)

    for invoice in invoices:
        retention_date = invoice.issue_date + timedelta(days=365 * 10)

        if datetime.now() < retention_date:
            return {
                'status': 'REJECTED',
                'reason': 'Faktury podlegają obowiązkowi przechowywania',
                'retention_until': retention_date
            }

    # 2. Jeśli okres minął - anonimizuj
    for invoice in invoices:
        anonymize_invoice_for_archive(invoice)

    return {
        'status': 'COMPLETED',
        'anonymized_invoices': len(invoices)
    }
```

---

## Kontrola Dostępu (RBAC)

### Role i Uprawnienia

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
    Sprawdź czy user ma uprawnienie
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
        raise PermissionError(f"User {user.username} nie ma uprawnień: {permission}")

    return True
```

---

## Certyfikaty SSL/TLS

### Połączenia do KSeF

```python
import ssl
import certifi

def secure_ksef_connection():
    """
    Zawsze używaj HTTPS z weryfikacją certyfikatu
    """
    session = requests.Session()

    # 1. Weryfikuj certyfikat (NIGDY verify=False)
    session.verify = certifi.where()

    # 2. Użyj silnych cipher suites
    session.mount('https://', requests.adapters.HTTPAdapter(
        max_retries=3,
        pool_connections=10,
        pool_maxsize=20
    ))

    # 3. Ustaw timeout
    session.request = lambda *args, **kwargs: \
        requests.Session.request(session, *args, timeout=30, **kwargs)

    return session
```

---

## Bezpieczne Praktyki Programistyczne

### 1. Unikaj dynamicznego wykonywania kodu

**❌ NIGDY nie używaj:**
- `eval()` lub `exec()` na danych wejściowych użytkownika lub danych zewnętrznych
- Wykonywania poleceń shell z konkatenacją stringów
- Dynamicznych zapytań SQL budowanych przez konkatenację stringów

**✅ ZAMIAST TEGO używaj:**
- Sparametryzowanych zapytań do bazy danych (zapobiega SQL injection)
- Walidowanych, sprawdzonych typowo danych wejściowych
- Strukturalnych wywołań API z odpowiednią obsługą argumentów
- Wbudowanych bibliotek i frameworków zaprojektowanych dla operacji księgowych

### 2. Walidacja Wejścia

```python
def validate_invoice_number(number):
    """Waliduj przed użyciem w zapytaniach"""
    # Tylko alfanumeryczne, myślniki, ukośniki
    import re
    if not re.match(r'^[A-Z0-9/-]+$', number):
        raise ValueError("Nieprawidłowy numer faktury")
    if len(number) > 50:
        raise ValueError("Numer faktury zbyt długi")
    return number
```

### 3. Principle of Least Privilege

```python
# Użytkownik bazy danych z minimalnymi uprawnieniami
DB_CONFIG = {
    'user': 'ksef_readonly',  # Tylko SELECT dla reportów
    'user': 'ksef_app',       # SELECT + INSERT + UPDATE dla app
    'user': 'ksef_admin',     # Wszystkie uprawnienia (tylko admin)
}
```

### 4. Używaj rozwiązań klasy enterprise

Dla produkcyjnych systemów księgowych:
- **Bazy danych:** Zarządzane usługi baz danych z automatycznymi backupami i point-in-time recovery
- **Monitoring:** Profesjonalne platformy monitoringu z możliwościami alertowania
- **Bezpieczeństwo:** Enterprise systemy zarządzania tożsamością i kontroli dostępu
- **Compliance:** Rozwiązania audit logging zaprojektowane dla danych finansowych

---

## Checklist Bezpieczeństwa

- [ ] Tokeny KSeF szyfrowane (Fernet/Vault)
- [ ] Biała lista VAT sprawdzana przed każdą płatnością
- [ ] Audit trail wszystkich operacji
- [ ] Backup 3-2-1 (daily)
- [ ] HTTPS z weryfikacją certyfikatu
- [ ] RBAC (kontrola dostępu)
- [ ] Retention policy zgodna z prawem (10 lat)
- [ ] RODO - anonimizacja po okresie przechowywania
- [ ] Monitoring i alerty
- [ ] Disaster recovery plan (testowany co kwartał)

---

**Compliance:** Wdrożenie powyższych praktyk wspiera zgodność z:
- Ustawą o VAT
- RODO / GDPR
- Ustawą o rachunkowości
- Normami ISO 27001 (opcjonalnie)
