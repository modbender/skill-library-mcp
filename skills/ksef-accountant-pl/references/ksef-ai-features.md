# Funkcje AI dla KSeF

**UWAGA OGÓLNA:** Cały kod w tym dokumencie to **koncepcyjna architektura referencyjna** — wzorce implementacyjne do adaptacji przez użytkownika w jego własnym systemie. Ten skill NIE uruchamia modeli ML, NIE wykonuje inferencji i NIE wymaga runtime'ów Python, sklearn, pandas ani żadnych innych zależności. Agent korzysta z tych wzorców wyłącznie jako bazy wiedzy do wyjaśniania algorytmów, projektowania pipeline'ów i pomocy w pisaniu kodu.

**Zależności wymagane do implementacji (NIE zależności tego skilla):** sklearn, pandas, numpy — do zainstalowania przez użytkownika w jego środowisku.

Wszystkie funkcje AI/ML mają charakter wspierający i wymagają nadzoru personelu księgowego. Wskaźniki wydajności są celami projektowymi i mogą się różnić. Systemy AI nie podejmują wiążących decyzji podatkowych.

---

## Klasyfikacja Kosztów

### Algorytm (wysokopoziomowy)

```python
def classify_expense(invoice_data):
    """
    Klasyfikacja kosztu na podstawie wielu źródeł danych
    """
    features = {
        'seller_name': invoice_data.seller_name,
        'item_names': [item.name for item in invoice_data.items],
        'pkwiu_codes': [item.pkwiu for item in invoice_data.items if item.pkwiu],
        'total_amount': invoice_data.total_gross,
        'seller_nip': invoice_data.seller_nip
    }

    # 1. Historia z kontrahentem (najwyższy priorytet)
    historical = get_historical_category(features['seller_nip'])
    if historical and historical.confidence > 0.9:
        return historical.category, historical.confidence

    # 2. Dopasowanie słów kluczowych
    keyword_match = match_keywords(features['item_names'])
    if keyword_match and keyword_match.confidence > 0.85:
        return keyword_match.category, keyword_match.confidence

    # 3. Model ML (Random Forest / Neural Network)
    ml_prediction = ml_model.predict(features)

    # 4. Flagowanie do review jeśli niska pewność
    if ml_prediction.confidence < 0.8:
        flag_for_manual_review(invoice_data)

    return ml_prediction.category, ml_prediction.confidence
```

### Kategorie Kosztów (Przykładowe)

```python
COST_CATEGORIES = {
    # Usługi obce
    400: "Usługi obce (ogólne)",
    401: "Usługi transportowe",
    402: "Usługi informatyczne (hosting, development, IT support)",
    403: "Usługi prawne i doradcze",
    404: "Usługi najmu i dzierżawy",
    405: "Usługi marketingowe i reklamowe",
    406: "Usługi księgowe",
    407: "Usługi konsultingowe",

    # Materiały i surowce
    500: "Materiały i surowce (ogólne)",
    501: "Energia, woda, paliwo",
    502: "Materiały biurowe",
    503: "Części zamienne",

    # Inne
    600: "Wynagrodzenia i pochodne",
    700: "Amortyzacja",
}
```

### Słowa Kluczowe (Przykłady)

```python
KEYWORDS = {
    402: ["hosting", "server", "cloud", "AWS", "Azure", "development",
          "programowanie", "IT support", "software", "licencja"],
    405: ["reklama", "marketing", "Google Ads", "Facebook Ads",
          "social media", "SEO", "content"],
    501: ["energia", "prąd", "gaz", "woda", "paliwo", "benzyna"],
    502: ["papier", "długopis", "toner", "biuro", "artykuły"],
}
```

### Trenowanie Modelu ML

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

class ExpenseClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=500)

    def train(self, historical_invoices):
        """
        Trenowanie na danych historycznych
        """
        # Przygotuj dane
        X_text = [
            f"{inv.seller_name} {' '.join(inv.item_names)}"
            for inv in historical_invoices
        ]
        X_vectors = self.vectorizer.fit_transform(X_text)

        y = [inv.category for inv in historical_invoices]

        # Trenuj model
        self.model.fit(X_vectors, y)

    def predict(self, invoice):
        """
        Predykcja kategorii
        """
        X_text = f"{invoice.seller_name} {' '.join(invoice.item_names)}"
        X_vector = self.vectorizer.transform([X_text])

        prediction = self.model.predict(X_vector)[0]
        probabilities = self.model.predict_proba(X_vector)[0]
        confidence = max(probabilities)

        return {
            'category': prediction,
            'confidence': confidence,
            'alternatives': self._get_alternatives(probabilities)
        }
```

---

## Wykrywanie Anomalii i Fraudu

### Detekcja Anomalii (Isolation Forest)

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False

    def extract_features(self, invoice):
        """Ekstrakcja cech do analizy"""
        return np.array([
            invoice.total_gross,
            len(invoice.items),
            invoice.items_avg_price,
            invoice.payment_term_days,
            invoice.hour_of_day,  # 0-23
            int(invoice.is_weekend),  # 0 lub 1
            invoice.seller_transaction_count,
            invoice.seller_avg_amount,
            invoice.amount_vs_avg_ratio  # aktualna / średnia
        ])

    def train(self, historical_invoices):
        """Trenowanie na danych historycznych"""
        features = [self.extract_features(inv) for inv in historical_invoices]
        self.model.fit(features)
        self.is_trained = True

    def detect(self, invoice):
        """Wykrycie anomalii"""
        if not self.is_trained:
            return {'anomaly': False, 'reason': 'Model nie wytrenowany'}

        features = self.extract_features(invoice)
        prediction = self.model.predict([features])[0]

        if prediction == -1:  # Anomalia
            return {
                'anomaly': True,
                'risk_level': 'HIGH',
                'reasons': self._analyze_reasons(invoice),
                'action': 'MANUAL_REVIEW_REQUIRED'
            }

        return {'anomaly': False}

    def _analyze_reasons(self, invoice):
        """Analiza przyczyn anomalii"""
        reasons = []

        if invoice.total_gross > invoice.seller_avg_amount * 3:
            reasons.append("Kwota 3x większa niż średnia od tego sprzedawcy")

        if invoice.is_weekend and invoice.hour_of_day < 6:
            reasons.append("Wystawiona w nocy w weekend (nietypowe)")

        if invoice.seller_transaction_count == 1:
            reasons.append("Pierwszy kontakt z tym sprzedawcą")

        if invoice.payment_term_days < 3:
            reasons.append("Bardzo krótki termin płatności (możliwy phishing)")

        return reasons
```

### Detekcja Phishing Invoices

```python
def detect_phishing_invoice(invoice):
    """
    Wykrywa potencjalne faktury phishingowe
    """
    score = 0
    reasons = []

    # 1. Podobna nazwa do znanego kontrahenta
    similar = find_similar_contractor_names(invoice.seller_name)
    for known_contractor in similar:
        if known_contractor.nip != invoice.seller_nip:
            score += 30
            reasons.append(f"Podobna nazwa do {known_contractor.name} ale inny NIP")

        if known_contractor.bank_account != invoice.bank_account:
            score += 40
            reasons.append("Inne konto bankowe niż znany kontrahent")

    # 2. Krótki termin płatności
    if invoice.payment_term_days <= 2:
        score += 20
        reasons.append("Bardzo krótki termin płatności (typowe dla phishingu)")

    # 3. Pierwszy kontakt
    if get_transaction_count(invoice.seller_nip) == 0:
        score += 10
        reasons.append("Pierwszy raz od tego sprzedawcy")

    # 4. Wysoka kwota przy pierwszym kontakcie
    if score > 0 and invoice.total_gross > 10000:
        score += 15
        reasons.append("Wysoka kwota przy pierwszym/podejrzanym kontakcie")

    if score >= 50:
        return {
            'phishing_detected': True,
            'risk': 'CRITICAL',
            'score': score,
            'reasons': reasons,
            'action': 'BLOCK_PAYMENT_AND_VERIFY'
        }

    return {'phishing_detected': False}
```

### Detekcja VAT Carousel

```python
def detect_vat_carousel(invoices, time_window_days=30):
    """
    Wykrywa potencjalne wzorce karuzeli VAT
    """
    # Buduj graf transakcji
    graph = build_transaction_graph(invoices)

    # Szukaj cykli (A → B → C → A)
    cycles = find_cycles(graph)

    suspicious = []
    for cycle in cycles:
        # Sprawdź podejrzane cechy
        if is_suspicious_cycle(cycle):
            suspicious.append({
                'cycle': cycle,
                'risk': 'CRITICAL',
                'participants': [node.nip for node in cycle],
                'total_value': sum(edge.amount for edge in cycle),
                'time_span_days': get_cycle_duration(cycle),
                'action': 'REPORT_TO_TAX_OFFICE'
            })

    return suspicious

def is_suspicious_cycle(cycle):
    """Czy cykl jest podejrzany?"""
    # 1. Cykl zamyka się w <30 dni
    if get_cycle_duration(cycle) > 30:
        return False

    # 2. Kwoty podobne (±10%)
    amounts = [edge.amount for edge in cycle]
    if max(amounts) / min(amounts) > 1.1:
        return False

    # 3. Ten sam towar/usługa
    items = [edge.item_description for edge in cycle]
    if not all_similar(items):
        return False

    return True
```

---

## Predykcja Cash Flow

### Model Predykcyjny

```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class CashFlowPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_training_data(self, historical_data):
        """
        Przygotowanie danych treningowych
        DataFrame z kolumnami:
        - invoice_due_date, invoice_amount, contractor_nip
        - payment_term_days, actual_payment_date, days_late
        """
        X = historical_data[[
            'invoice_amount',
            'payment_term_days',
            'contractor_avg_days_late',
            'contractor_payment_reliability',  # % w terminie
            'month',
            'is_end_of_quarter'
        ]]

        y = historical_data['days_late']

        return X, y

    def train(self, historical_data):
        X, y = self.prepare_training_data(historical_data)
        self.model.fit(X, y)

    def predict_payment_date(self, invoice):
        """Przewiduj rzeczywistą datę płatności"""
        contractor_stats = get_contractor_stats(invoice.buyer_nip)

        features = pd.DataFrame([{
            'invoice_amount': invoice.total_gross,
            'payment_term_days': invoice.payment_term_days,
            'contractor_avg_days_late': contractor_stats['avg_days_late'],
            'contractor_payment_reliability': contractor_stats['reliability'],
            'month': invoice.issue_date.month,
            'is_end_of_quarter': invoice.issue_date.month in [3, 6, 9, 12]
        }])

        predicted_days_late = self.model.predict(features)[0]
        predicted_date = invoice.payment_due_date + timedelta(days=int(predicted_days_late))

        return {
            'predicted_payment_date': predicted_date,
            'expected_days_late': int(predicted_days_late),
            'confidence': self._calculate_confidence(features)
        }

    def predict_monthly_cash_flow(self, year, month):
        """Prognoza miesięczna"""
        # Faktury sprzedaży z terminem w tym miesiącu
        sales_invoices = get_invoices_due_in_month(year, month, type='sales')

        predicted_income = 0
        for invoice in sales_invoices:
            prediction = self.predict_payment_date(invoice)
            # Tylko jeśli przewidywana płatność w tym miesiącu
            if prediction['predicted_payment_date'].month == month:
                predicted_income += invoice.total_gross

        # Faktury zakupowe
        purchase_invoices = get_invoices_due_in_month(year, month, type='purchases')
        predicted_expenses = sum(inv.total_gross for inv in purchase_invoices)

        return {
            'month': f"{year}-{month:02d}",
            'predicted_income': predicted_income,
            'predicted_expenses': predicted_expenses,
            'net_cash_flow': predicted_income - predicted_expenses,
            'note': 'Predykcja ma charakter szacunkowy'
        }
```

### Statystyki Kontrahenta

```python
def get_contractor_stats(nip):
    """
    Oblicz statystyki płatności dla kontrahenta
    """
    invoices = get_all_invoices_for_contractor(nip)

    if not invoices:
        return {
            'avg_days_late': 0,
            'reliability': 1.0,  # Brak historii = optymistyczne założenie
            'total_invoices': 0
        }

    days_late_list = []
    paid_on_time = 0

    for inv in invoices:
        if inv.payment_date:
            days_late = (inv.payment_date - inv.payment_due_date).days
            days_late_list.append(max(0, days_late))  # Tylko dodatnie

            if days_late <= 0:
                paid_on_time += 1

    return {
        'avg_days_late': sum(days_late_list) / len(days_late_list),
        'reliability': paid_on_time / len(invoices),
        'total_invoices': len(invoices),
        'max_days_late': max(days_late_list) if days_late_list else 0
    }
```

---

## Best Practices dla AI

### 1. Ciągłe Uczenie (Continuous Learning)

```python
def retrain_models_monthly():
    """
    Retrenuj modele co miesiąc na świeżych danych
    """
    # Pobierz dane z ostatnich 12 miesięcy
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    historical_data = get_invoices(start_date, end_date)

    # Retrenuj klasyfikator kosztów
    expense_classifier.train(historical_data)

    # Retrenuj detektor anomalii
    fraud_detector.train(historical_data)

    # Retrenuj predyktor cash flow
    cash_flow_predictor.train(historical_data)

    save_models()  # Zapisz do dysku
```

### 2. Human-in-the-Loop

```python
def classify_with_review(invoice):
    """
    Klasyfikacja z flagowaniem do review
    """
    prediction = expense_classifier.predict(invoice)

    if prediction['confidence'] < 0.8:
        # Niska pewność → human review
        task = create_review_task(
            invoice=invoice,
            suggested_category=prediction['category'],
            confidence=prediction['confidence'],
            alternatives=prediction['alternatives']
        )
        return {
            'category': None,  # Czekaj na review
            'status': 'PENDING_REVIEW',
            'task_id': task.id
        }

    # Wysoka pewność → auto-classify
    return {
        'category': prediction['category'],
        'status': 'AUTO_CLASSIFIED',
        'confidence': prediction['confidence']
    }
```

### 3. Audit Trail dla AI

```python
def log_ai_decision(invoice, prediction, action):
    """
    Loguj decyzje AI dla audytu
    """
    ai_audit_log.insert({
        'timestamp': datetime.now(),
        'invoice_id': invoice.id,
        'model_name': 'ExpenseClassifier',
        'model_version': '2.1',
        'prediction': prediction,
        'confidence': prediction['confidence'],
        'action_taken': action,
        'reviewed_by_human': action == 'MANUAL_REVIEW'
    })
```

---

**Ostrzeżenie końcowe:** Wszystkie funkcje AI wymagają regularnego monitorowania, walidacji i nadzoru ze strony wykwalifikowanego personelu. Nie należy polegać wyłącznie na automatycznych decyzjach w sprawach podatkowych i księgowych.

**Przypomnienie:** Powyższe przykłady kodu to architektura referencyjna. Ten skill nie zawiera wytrenowanych modeli, artefaktów ML ani plików wykonywalnych. Implementacja wymaga zainstalowania zależności (sklearn, pandas, numpy) i wytrenowania modeli na danych użytkownika w jego własnym środowisku.
