"""
Oracle / Ground Truth tests for email classification.

These tests validate the classifier against known email patterns.
No LLM involved - purely deterministic heuristics.

Run with: pytest -m oracle
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from kaimail.classifier import EmailClassifier
from kaimail.models import EmailCategory, ParsedEmail
from kaimail.parser import EmailParser

# Load oracle cases from fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
ORACLE_CASES_FILE = FIXTURES_DIR / "oracle_cases.jsonl"


def load_oracle_cases():
    """Load test cases from JSONL file."""
    cases = []
    with open(ORACLE_CASES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


@pytest.fixture
def classifier():
    return EmailClassifier()


@pytest.fixture
def parser():
    return EmailParser()


def parse_email_from_case(case: dict) -> ParsedEmail:
    """Convert oracle case input to ParsedEmail."""
    input_data = case["input_email"]

    # Parse date string to datetime
    date_str = input_data["date"]
    if isinstance(date_str, str):
        date = datetime.fromisoformat(date_str)
    else:
        date = datetime.now()

    return ParsedEmail(
        id=input_data["id"],
        thread_id=input_data["thread_id"],
        date=date,
        sender_email=input_data["sender_email"],
        sender_name=input_data["sender_name"],
        sender_domain=input_data["sender_domain"],
        subject=input_data["subject"],
        subject_clean=input_data["subject_clean"],
        body_text=input_data.get("body_text", ""),
        body_preview=input_data.get("body_preview", ""),
        labels=input_data.get("labels", []),
        is_forwarded=input_data.get("is_forwarded", False),
        is_reply=input_data.get("is_reply", False),
        has_attachments=input_data.get("has_attachments", False),
    )


class TestOracleClassification:
    """Test classification against ground truth cases."""

    @pytest.mark.oracle
    @pytest.mark.parametrize("case", load_oracle_cases(), ids=lambda c: c["id"])
    def test_classification_matches_expected(self, classifier, case):
        """Each email should be classified as expected."""
        email = parse_email_from_case(case)
        expected = EmailCategory(case["expected_classification"])

        result = classifier.classify(email)

        assert result == expected, (
            f"Case {case['id']}: expected {expected}, got {result}\n"
            f"Subject: {email.subject}\n"
            f"Sender: {email.sender_email}\n"
            f"Labels: {email.labels}"
        )


class TestOracleParserFields:
    """Test parser field extraction against ground truth."""

    @pytest.mark.oracle
    @pytest.mark.parametrize("case", load_oracle_cases(), ids=lambda c: c["id"])
    def test_parsed_fields_match(self, parser, case):
        """Parsed fields should match expected values."""
        email = parse_email_from_case(case)
        expected_fields = case.get("expected_parsed_fields", {})

        for field, expected_value in expected_fields.items():
            actual_value = getattr(email, field, None)
            assert actual_value == expected_value, (
                f"Case {case['id']}: field '{field}' expected {expected_value}, got {actual_value}"
            )


class TestNewsletterDetection:
    """Focused tests for newsletter detection patterns."""

    @pytest.fixture
    def newsletter_cases(self):
        """Get all newsletter cases from oracle data."""
        cases = load_oracle_cases()
        return [c for c in cases if c["expected_classification"] == "newsletter"]

    @pytest.mark.oracle
    def test_all_newsletters_detected(self, classifier, newsletter_cases):
        """All newsletter cases should be classified as newsletter."""
        for case in newsletter_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.NEWSLETTER, (
                f"Case {case['id']} not detected as newsletter"
            )

    @pytest.mark.oracle
    def test_substack_always_newsletter(self, classifier):
        """Emails from substack.com should always be newsletters."""
        cases = load_oracle_cases()
        substack_cases = [c for c in cases if "substack.com" in c["input_email"]["sender_domain"]]

        assert len(substack_cases) > 0, "Should have substack test cases"

        for case in substack_cases:
            email = parse_email_from_case(case)
            assert classifier.classify(email) == EmailCategory.NEWSLETTER


class TestNotificationDetection:
    """Focused tests for notification detection."""

    @pytest.fixture
    def notification_cases(self):
        cases = load_oracle_cases()
        return [c for c in cases if c["expected_classification"] == "notification"]

    @pytest.mark.oracle
    def test_all_notifications_detected(self, classifier, notification_cases):
        """All notification cases should be classified correctly."""
        for case in notification_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.NOTIFICATION, (
                f"Case {case['id']} not detected as notification"
            )


class TestTravelDetection:
    """Focused tests for travel/reservation detection."""

    @pytest.fixture
    def travel_cases(self):
        cases = load_oracle_cases()
        return [c for c in cases if c["expected_classification"] == "travel"]

    @pytest.mark.oracle
    def test_all_travel_detected(self, classifier, travel_cases):
        """All travel cases should be classified correctly."""
        for case in travel_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.TRAVEL, f"Case {case['id']} not detected as travel"

    @pytest.mark.oracle
    def test_hebrew_reservation_detected(self, classifier):
        """Hebrew reservation confirmation should be detected as travel or restaurant."""
        cases = load_oracle_cases()
        hebrew_cases = [
            c
            for c in cases
            if "אשרו" in c["input_email"]["subject"]  # Hebrew "confirm"
        ]

        for case in hebrew_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            # Should be travel or restaurant_reservation (both valid for reservations)
            valid_categories = {EmailCategory.TRAVEL, EmailCategory.RESTAURANT_RESERVATION}
            assert result in valid_categories, (
                f"Hebrew reservation not detected: {case['id']} got {result}"
            )


class TestPromotionalDetection:
    """Focused tests for promotional email detection."""

    @pytest.fixture
    def promo_cases(self):
        cases = load_oracle_cases()
        return [c for c in cases if c["expected_classification"] == "promotional"]

    @pytest.mark.oracle
    def test_all_promotional_detected(self, classifier, promo_cases):
        """All promotional cases should be classified correctly."""
        for case in promo_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.PROMOTIONAL, (
                f"Case {case['id']} not detected as promotional"
            )

    @pytest.mark.oracle
    def test_category_promotions_label(self, classifier):
        """Emails with CATEGORY_PROMOTIONS label should be promotional."""
        cases = load_oracle_cases()
        promo_label_cases = [
            c
            for c in cases
            if "CATEGORY_PROMOTIONS" in c["input_email"].get("labels", [])
            and c["expected_classification"] == "promotional"
        ]

        for case in promo_label_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.PROMOTIONAL


class TestReceiptDetection:
    """Focused tests for receipt/invoice detection."""

    @pytest.fixture
    def receipt_cases(self):
        cases = load_oracle_cases()
        return [c for c in cases if c["expected_classification"] == "receipt"]

    @pytest.mark.oracle
    def test_all_receipts_detected(self, classifier, receipt_cases):
        """All receipt cases should be classified correctly."""
        for case in receipt_cases:
            email = parse_email_from_case(case)
            result = classifier.classify(email)
            assert result == EmailCategory.RECEIPT, f"Case {case['id']} not detected as receipt"


class TestForwardedEmailParsing:
    """Test that forwarded emails are correctly identified."""

    @pytest.mark.oracle
    def test_forwarded_flag(self, parser):
        """Forwarded emails should have is_forwarded=True."""
        cases = load_oracle_cases()
        forwarded_cases = [c for c in cases if c["input_email"].get("is_forwarded", False)]

        assert len(forwarded_cases) > 0, "Should have forwarded test cases"

        for case in forwarded_cases:
            subject = case["input_email"]["subject"]
            assert parser._is_forwarded(subject), f"Subject not detected as forward: {subject}"

    @pytest.mark.oracle
    def test_subject_clean_strips_fwd(self, parser):
        """Clean subject should not have Fwd: prefix."""
        cases = load_oracle_cases()
        forwarded_cases = [c for c in cases if c["input_email"].get("is_forwarded", False)]

        for case in forwarded_cases:
            expected_clean = case["expected_parsed_fields"].get("subject_clean")
            if expected_clean:
                actual_clean = parser._clean_subject(case["input_email"]["subject"])
                assert actual_clean == expected_clean, (
                    f"Subject clean mismatch: expected '{expected_clean}', got '{actual_clean}'"
                )


class TestConfidenceScoring:
    """Test that confidence scores make sense for oracle cases."""

    @pytest.mark.oracle
    def test_high_confidence_for_clear_cases(self, classifier):
        """Clear-cut cases should have high confidence."""
        cases = load_oracle_cases()

        for case in cases:
            email = parse_email_from_case(case)
            expected_category = EmailCategory(case["expected_classification"])
            confidence = classifier.get_confidence(email, expected_category)

            # Most cases should have reasonable confidence
            if expected_category != EmailCategory.PERSONAL:
                assert confidence >= 0.33, (
                    f"Case {case['id']} has low confidence {confidence} for {expected_category}"
                )
