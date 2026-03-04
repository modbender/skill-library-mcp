# AI Features for KSeF

**GENERAL NOTE:** All code in this document is **conceptual reference architecture** — implementation patterns for the user to adapt in their own system. This skill does NOT run ML models, does NOT perform inference and does NOT require Python, sklearn, pandas or any other runtime dependencies. The agent uses these patterns solely as a knowledge base for explaining algorithms, designing pipelines and helping write code.

**Dependencies required for implementation (NOT dependencies of this skill):** sklearn, pandas, numpy — to be installed by the user in their environment.

All AI/ML features are supportive in nature and require supervision by accounting staff. Performance metrics are design goals and may vary. AI systems do not make binding tax decisions.

---

## Expense Classification

### Algorithm (High-Level)

```python
def classify_expense(invoice_data):
    """
    Expense classification based on multiple data sources
    """
    features = {
        'seller_name': invoice_data.seller_name,
        'item_names': [item.name for item in invoice_data.items],
        'pkwiu_codes': [item.pkwiu for item in invoice_data.items if item.pkwiu],
        'total_amount': invoice_data.total_gross,
        'seller_nip': invoice_data.seller_nip
    }

    # 1. Contractor history (highest priority)
    historical = get_historical_category(features['seller_nip'])
    if historical and historical.confidence > 0.9:
        return historical.category, historical.confidence

    # 2. Keyword matching
    keyword_match = match_keywords(features['item_names'])
    if keyword_match and keyword_match.confidence > 0.85:
        return keyword_match.category, keyword_match.confidence

    # 3. ML model (Random Forest / Neural Network)
    ml_prediction = ml_model.predict(features)

    # 4. Flag for review if low confidence
    if ml_prediction.confidence < 0.8:
        flag_for_manual_review(invoice_data)

    return ml_prediction.category, ml_prediction.confidence
```

### Expense Categories (Examples)

```python
COST_CATEGORIES = {
    # External services
    400: "External services (general)",
    401: "Transport services",
    402: "IT services (hosting, development, IT support)",
    403: "Legal and advisory services",
    404: "Rental and lease services",
    405: "Marketing and advertising services",
    406: "Accounting services",
    407: "Consulting services",

    # Materials and raw materials
    500: "Materials and raw materials (general)",
    501: "Energy, water, fuel",
    502: "Office supplies",
    503: "Spare parts",

    # Other
    600: "Salaries and related costs",
    700: "Depreciation",
}
```

### Keywords (Examples)

```python
KEYWORDS = {
    402: ["hosting", "server", "cloud", "AWS", "Azure", "development",
          "programming", "IT support", "software", "license"],
    405: ["advertising", "marketing", "Google Ads", "Facebook Ads",
          "social media", "SEO", "content"],
    501: ["energy", "electricity", "gas", "water", "fuel", "gasoline"],
    502: ["paper", "pen", "toner", "office", "supplies"],
}
```

### ML Model Training

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

class ExpenseClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=500)

    def train(self, historical_invoices):
        """
        Training on historical data
        """
        # Prepare data
        X_text = [
            f"{inv.seller_name} {' '.join(inv.item_names)}"
            for inv in historical_invoices
        ]
        X_vectors = self.vectorizer.fit_transform(X_text)

        y = [inv.category for inv in historical_invoices]

        # Train model
        self.model.fit(X_vectors, y)

    def predict(self, invoice):
        """
        Category prediction
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

## Anomaly and Fraud Detection

### Anomaly Detection (Isolation Forest)

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False

    def extract_features(self, invoice):
        """Feature extraction for analysis"""
        return np.array([
            invoice.total_gross,
            len(invoice.items),
            invoice.items_avg_price,
            invoice.payment_term_days,
            invoice.hour_of_day,  # 0-23
            int(invoice.is_weekend),  # 0 or 1
            invoice.seller_transaction_count,
            invoice.seller_avg_amount,
            invoice.amount_vs_avg_ratio  # current / average
        ])

    def train(self, historical_invoices):
        """Training on historical data"""
        features = [self.extract_features(inv) for inv in historical_invoices]
        self.model.fit(features)
        self.is_trained = True

    def detect(self, invoice):
        """Anomaly detection"""
        if not self.is_trained:
            return {'anomaly': False, 'reason': 'Model not trained'}

        features = self.extract_features(invoice)
        prediction = self.model.predict([features])[0]

        if prediction == -1:  # Anomaly
            return {
                'anomaly': True,
                'risk_level': 'HIGH',
                'reasons': self._analyze_reasons(invoice),
                'action': 'MANUAL_REVIEW_REQUIRED'
            }

        return {'anomaly': False}

    def _analyze_reasons(self, invoice):
        """Analyze anomaly reasons"""
        reasons = []

        if invoice.total_gross > invoice.seller_avg_amount * 3:
            reasons.append("Amount 3x greater than average from this seller")

        if invoice.is_weekend and invoice.hour_of_day < 6:
            reasons.append("Issued at night on weekend (unusual)")

        if invoice.seller_transaction_count == 1:
            reasons.append("First contact with this seller")

        if invoice.payment_term_days < 3:
            reasons.append("Very short payment term (possible phishing)")

        return reasons
```

### Phishing Invoice Detection

```python
def detect_phishing_invoice(invoice):
    """
    Detects potential phishing invoices
    """
    score = 0
    reasons = []

    # 1. Similar name to known contractor
    similar = find_similar_contractor_names(invoice.seller_name)
    for known_contractor in similar:
        if known_contractor.nip != invoice.seller_nip:
            score += 30
            reasons.append(f"Similar name to {known_contractor.name} but different NIP")

        if known_contractor.bank_account != invoice.bank_account:
            score += 40
            reasons.append("Different bank account than known contractor")

    # 2. Short payment term
    if invoice.payment_term_days <= 2:
        score += 20
        reasons.append("Very short payment term (typical for phishing)")

    # 3. First contact
    if get_transaction_count(invoice.seller_nip) == 0:
        score += 10
        reasons.append("First time from this seller")

    # 4. High amount on first contact
    if score > 0 and invoice.total_gross > 10000:
        score += 15
        reasons.append("High amount on first/suspicious contact")

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

### VAT Carousel Detection

```python
def detect_vat_carousel(invoices, time_window_days=30):
    """
    Detects potential VAT carousel patterns
    """
    # Build transaction graph
    graph = build_transaction_graph(invoices)

    # Look for cycles (A -> B -> C -> A)
    cycles = find_cycles(graph)

    suspicious = []
    for cycle in cycles:
        # Check suspicious characteristics
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
    """Is the cycle suspicious?"""
    # 1. Cycle closes within <30 days
    if get_cycle_duration(cycle) > 30:
        return False

    # 2. Similar amounts (+/-10%)
    amounts = [edge.amount for edge in cycle]
    if max(amounts) / min(amounts) > 1.1:
        return False

    # 3. Same goods/services
    items = [edge.item_description for edge in cycle]
    if not all_similar(items):
        return False

    return True
```

---

## Cash Flow Prediction

### Predictive Model

```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

class CashFlowPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_training_data(self, historical_data):
        """
        Training data preparation
        DataFrame with columns:
        - invoice_due_date, invoice_amount, contractor_nip
        - payment_term_days, actual_payment_date, days_late
        """
        X = historical_data[[
            'invoice_amount',
            'payment_term_days',
            'contractor_avg_days_late',
            'contractor_payment_reliability',  # % on time
            'month',
            'is_end_of_quarter'
        ]]

        y = historical_data['days_late']

        return X, y

    def train(self, historical_data):
        X, y = self.prepare_training_data(historical_data)
        self.model.fit(X, y)

    def predict_payment_date(self, invoice):
        """Predict actual payment date"""
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
        """Monthly forecast"""
        # Sales invoices due in this month
        sales_invoices = get_invoices_due_in_month(year, month, type='sales')

        predicted_income = 0
        for invoice in sales_invoices:
            prediction = self.predict_payment_date(invoice)
            # Only if predicted payment is in this month
            if prediction['predicted_payment_date'].month == month:
                predicted_income += invoice.total_gross

        # Purchase invoices
        purchase_invoices = get_invoices_due_in_month(year, month, type='purchases')
        predicted_expenses = sum(inv.total_gross for inv in purchase_invoices)

        return {
            'month': f"{year}-{month:02d}",
            'predicted_income': predicted_income,
            'predicted_expenses': predicted_expenses,
            'net_cash_flow': predicted_income - predicted_expenses,
            'note': 'Prediction is an estimate'
        }
```

### Contractor Statistics

```python
def get_contractor_stats(nip):
    """
    Calculate payment statistics for a contractor
    """
    invoices = get_all_invoices_for_contractor(nip)

    if not invoices:
        return {
            'avg_days_late': 0,
            'reliability': 1.0,  # No history = optimistic assumption
            'total_invoices': 0
        }

    days_late_list = []
    paid_on_time = 0

    for inv in invoices:
        if inv.payment_date:
            days_late = (inv.payment_date - inv.payment_due_date).days
            days_late_list.append(max(0, days_late))  # Only positive

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

## AI Best Practices

### 1. Continuous Learning

```python
def retrain_models_monthly():
    """
    Retrain models monthly on fresh data
    """
    # Get data from last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    historical_data = get_invoices(start_date, end_date)

    # Retrain expense classifier
    expense_classifier.train(historical_data)

    # Retrain anomaly detector
    fraud_detector.train(historical_data)

    # Retrain cash flow predictor
    cash_flow_predictor.train(historical_data)

    save_models()  # Save to disk
```

### 2. Human-in-the-Loop

```python
def classify_with_review(invoice):
    """
    Classification with flagging for review
    """
    prediction = expense_classifier.predict(invoice)

    if prediction['confidence'] < 0.8:
        # Low confidence -> human review
        task = create_review_task(
            invoice=invoice,
            suggested_category=prediction['category'],
            confidence=prediction['confidence'],
            alternatives=prediction['alternatives']
        )
        return {
            'category': None,  # Wait for review
            'status': 'PENDING_REVIEW',
            'task_id': task.id
        }

    # High confidence -> auto-classify
    return {
        'category': prediction['category'],
        'status': 'AUTO_CLASSIFIED',
        'confidence': prediction['confidence']
    }
```

### 3. Audit Trail for AI

```python
def log_ai_decision(invoice, prediction, action):
    """
    Log AI decisions for audit
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

**Final warning:** All AI features require regular monitoring, validation and supervision by qualified staff. Do not rely solely on automated decisions in tax and accounting matters.

**Reminder:** The code examples above are reference architecture. This skill does not contain trained models, ML artifacts or executable files. Implementation requires installing dependencies (sklearn, pandas, numpy) and training models on user data in their own environment.
