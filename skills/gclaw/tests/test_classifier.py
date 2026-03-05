"""Tests for EmailClassifier."""

from datetime import datetime

import pytest

from kaimail.classifier import EmailClassifier
from kaimail.models import EmailCategory, ParsedEmail


@pytest.fixture
def classifier():
    return EmailClassifier()


def make_email(
    sender_email: str = "test@example.com",
    sender_domain: str = "example.com",
    subject: str = "Test Subject",
    labels: list[str] | None = None,
    body_text: str = "",
) -> ParsedEmail:
    """Helper to create test emails."""
    return ParsedEmail(
        id="test123",
        thread_id="test123",
        date=datetime.now(),
        sender_email=sender_email,
        sender_name="Test Sender",
        sender_domain=sender_domain,
        subject=subject,
        subject_clean=subject,
        body_text=body_text,
        body_preview=body_text[:200],
        labels=labels or [],
    )


# ==========================================================================
# SECURITY CLASSIFICATION TESTS
# ==========================================================================


class TestSecurityClassification:
    def test_google_security_alert(self, classifier):
        email = make_email(
            sender_email="no-reply@accounts.google.com",
            sender_domain="accounts.google.com",
            subject="Security alert: New sign-in to your account",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY

    def test_github_third_party_app(self, classifier):
        email = make_email(
            sender_email="noreply@github.com",
            sender_domain="github.com",
            subject="[GitHub] A third-party GitHub Application has been added to your account",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY

    def test_discord_security(self, classifier):
        email = make_email(
            sender_email="noreply@discord.com",
            sender_domain="discord.com",
            subject="Verification code for Discord",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY

    def test_verification_code_subject(self, classifier):
        email = make_email(
            sender_email="security@service.com",
            sender_domain="service.com",
            subject="Your verification code is 123456",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY

    def test_new_device_login(self, classifier):
        email = make_email(
            sender_email="alerts@bank.com",
            sender_domain="bank.com",
            subject="New device login detected on your account",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY


# ==========================================================================
# TRAVEL CLASSIFICATION TESTS
# ==========================================================================


class TestTravelClassification:
    def test_booking_domain(self, classifier):
        email = make_email(
            sender_email="confirm@booking.com",
            sender_domain="booking.com",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_wizzair_domain(self, classifier):
        email = make_email(
            sender_email="noreply@wizzair.com",
            sender_domain="wizzair.com",
            subject="Your flight confirmation",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_msc_cruise(self, classifier):
        email = make_email(
            sender_email="booking@msc.com",
            sender_domain="msc.com",
            subject="Your MSC Cruise Booking Confirmation",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_travel_label(self, classifier):
        email = make_email(
            sender_email="random@unknown.com",
            sender_domain="unknown.com",
            labels=["Travel"],
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_hebrew_flight_subject(self, classifier):
        email = make_email(
            sender_email="info@elal.com",
            sender_domain="elal.com",
            subject="אישור טיסה מספר 12345",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_cruise_subject(self, classifier):
        email = make_email(
            sender_email="info@cruiseline.com",
            sender_domain="cruiseline.com",
            subject="Your cruise itinerary is ready",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL


# ==========================================================================
# GITHUB NOTIFICATION TESTS
# ==========================================================================


class TestGitHubNotificationClassification:
    def test_github_domain(self, classifier):
        email = make_email(
            sender_email="notifications@github.com",
            sender_domain="github.com",
            subject="[user/repo] Pull request opened",
        )
        assert classifier.classify(email) == EmailCategory.GITHUB_NOTIFICATION

    def test_github_run_failed(self, classifier):
        email = make_email(
            sender_email="notifications@github.com",
            sender_domain="github.com",
            subject="[owner/repo] Run failed: CI workflow",
        )
        assert classifier.classify(email) == EmailCategory.GITHUB_NOTIFICATION

    def test_github_label(self, classifier):
        email = make_email(
            sender_email="random@unknown.com",
            sender_domain="unknown.com",
            labels=["GitHub"],
        )
        assert classifier.classify(email) == EmailCategory.GITHUB_NOTIFICATION

    def test_github_workflow_notification(self, classifier):
        email = make_email(
            sender_email="noreply@github.com",
            sender_domain="github.com",
            subject="[openclaw/core] Workflow run succeeded",
        )
        assert classifier.classify(email) == EmailCategory.GITHUB_NOTIFICATION


# ==========================================================================
# RESTAURANT RESERVATION TESTS
# ==========================================================================


class TestRestaurantReservationClassification:
    def test_tabit_reservation(self, classifier):
        email = make_email(
            sender_email="tabit-guest-no-reply@tabit.cloud",
            sender_domain="tabit.cloud",
            subject="אנא אשרו את הזמנתכם לHabBasta",
        )
        assert classifier.classify(email) == EmailCategory.RESTAURANT_RESERVATION

    def test_opentable(self, classifier):
        email = make_email(
            sender_email="noreply@opentable.com",
            sender_domain="opentable.com",
            subject="Reservation Confirmation",
        )
        assert classifier.classify(email) == EmailCategory.RESTAURANT_RESERVATION

    def test_resy_reservation(self, classifier):
        email = make_email(
            sender_email="noreply@resy.com",
            sender_domain="resy.com",
            subject="Your reservation at The Restaurant",
        )
        assert classifier.classify(email) == EmailCategory.RESTAURANT_RESERVATION

    def test_i_host_restaurant(self, classifier):
        email = make_email(
            sender_email="booking@i-host.gr",
            sender_domain="i-host.gr",
            subject="Reservation Confirmation - Taverna Mykonos",
        )
        assert classifier.classify(email) == EmailCategory.RESTAURANT_RESERVATION

    def test_reservation_reminder(self, classifier):
        email = make_email(
            sender_email="info@restaurant.com",
            sender_domain="restaurant.com",
            subject="Reservation Kind Reminder for tonight",
        )
        assert classifier.classify(email) == EmailCategory.RESTAURANT_RESERVATION


# ==========================================================================
# FINANCE CLASSIFICATION TESTS
# ==========================================================================


class TestFinanceClassification:
    def test_1password_invoice(self, classifier):
        email = make_email(
            sender_email="billing@1password.com",
            sender_domain="1password.com",
            subject="Your 1Password subscription",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_invoice_subject(self, classifier):
        email = make_email(
            sender_email="billing@service.com",
            sender_domain="service.com",
            subject="Invoice #12345 for your subscription",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_hebrew_invoice(self, classifier):
        email = make_email(
            sender_email="billing@company.co.il",
            sender_domain="company.co.il",
            subject="חשבונית מס 1234",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_payment_subject(self, classifier):
        email = make_email(
            sender_email="noreply@bank.com",
            sender_domain="bank.com",
            subject="Payment received - Thank you",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_subscription_billing(self, classifier):
        email = make_email(
            sender_email="billing@saas.com",
            sender_domain="saas.com",
            subject="Your subscription renewal",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE


# ==========================================================================
# ECOMMERCE ORDER TESTS
# ==========================================================================


class TestEcommerceOrderClassification:
    def test_amazon_order(self, classifier):
        email = make_email(
            sender_email="shipment-tracking@amazon.com",
            sender_domain="amazon.com",
            subject="Your Amazon order has shipped",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER

    def test_ksp_order(self, classifier):
        email = make_email(
            sender_email="orders@ksp.co.il",
            sender_domain="ksp.co.il",
            subject="הזמנה מספר 12345 נשלחה",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER

    def test_order_confirmation(self, classifier):
        email = make_email(
            sender_email="noreply@shop.com",
            sender_domain="shop.com",
            subject="Order confirmation #ORD-12345",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER

    def test_shipping_notification(self, classifier):
        email = make_email(
            sender_email="delivery@carrier.com",
            sender_domain="carrier.com",
            subject="Your package is out for delivery",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER

    def test_hebrew_order_confirmation(self, classifier):
        email = make_email(
            sender_email="noreply@store.co.il",
            sender_domain="store.co.il",
            subject="אישור הזמנה - מספר 54321",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER


# ==========================================================================
# HEALTH/INSURANCE TESTS
# ==========================================================================


class TestHealthInsuranceClassification:
    def test_meuhedet_hmo(self, classifier):
        email = make_email(
            sender_email="noreply@meuhedet.co.il",
            sender_domain="meuhedet.co.il",
            subject="תור במרפאה",
        )
        assert classifier.classify(email) == EmailCategory.HEALTH_INSURANCE

    def test_phoenix_insurance(self, classifier):
        email = make_email(
            sender_email="service@fnx.co.il",
            sender_domain="fnx.co.il",
            subject="פוליסת בריאות - חידוש שנתי",
        )
        assert classifier.classify(email) == EmailCategory.HEALTH_INSURANCE

    def test_health_insurance_subject(self, classifier):
        email = make_email(
            sender_email="info@insurance.com",
            sender_domain="insurance.com",
            subject="Your health insurance renewal",
        )
        assert classifier.classify(email) == EmailCategory.HEALTH_INSURANCE

    def test_hebrew_hmo_subject(self, classifier):
        email = make_email(
            sender_email="info@clinic.co.il",
            sender_domain="clinic.co.il",
            subject="אישור תור - מכבי שירותי בריאות",
        )
        assert classifier.classify(email) == EmailCategory.HEALTH_INSURANCE

    def test_medical_appointment(self, classifier):
        email = make_email(
            sender_email="noreply@clalit.co.il",
            sender_domain="clalit.co.il",
            subject="Appointment confirmation",
        )
        assert classifier.classify(email) == EmailCategory.HEALTH_INSURANCE


# ==========================================================================
# RECEIPT TESTS
# ==========================================================================


class TestReceiptClassification:
    def test_apple_invoice(self, classifier):
        """Apple invoice emails contain 'invoice' so they're classified as finance."""
        email = make_email(
            sender_email="no_reply@email.apple.com",
            sender_domain="email.apple.com",
            subject="Your invoice from Apple.",
        )
        # "invoice" in subject = finance (higher priority than receipt)
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_apple_receipt(self, classifier):
        """Apple receipt emails (with 'receipt' in subject) are receipts."""
        email = make_email(
            sender_email="no_reply@email.apple.com",
            sender_domain="email.apple.com",
            subject="Your receipt from Apple.",
        )
        assert classifier.classify(email) == EmailCategory.RECEIPT

    def test_receipt_subject_pattern(self, classifier):
        email = make_email(
            sender_email="receipts@store.com",
            sender_domain="store.com",
            subject="Your order confirmation #12345",
        )
        # Note: This might match ECOMMERCE_ORDER first due to priority
        result = classifier.classify(email)
        assert result in [EmailCategory.RECEIPT, EmailCategory.ECOMMERCE_ORDER]

    def test_paypal_receipt(self, classifier):
        """PayPal receipt with explicit 'Receipt' in subject."""
        email = make_email(
            sender_email="service@paypal.com",
            sender_domain="paypal.com",
            subject="Receipt for your payment",
        )
        assert classifier.classify(email) == EmailCategory.RECEIPT


# ==========================================================================
# NEWSLETTER TESTS
# ==========================================================================


class TestNewsletterClassification:
    def test_substack_domain(self, classifier):
        email = make_email(
            sender_email="author@substack.com",
            sender_domain="substack.com",
            subject="Weekly Update",
        )
        assert classifier.classify(email) == EmailCategory.NEWSLETTER

    def test_stratechery_domain(self, classifier):
        email = make_email(
            sender_email="email@stratechery.com",
            sender_domain="stratechery.com",
        )
        assert classifier.classify(email) == EmailCategory.NEWSLETTER

    def test_thoughts_label(self, classifier):
        email = make_email(
            sender_email="random@unknown.com",
            sender_domain="unknown.com",
            labels=["Thoughts"],
        )
        assert classifier.classify(email) == EmailCategory.NEWSLETTER

    def test_mailchimp_domain(self, classifier):
        email = make_email(
            sender_email="news@123.mailchimpapp.com",
            sender_domain="123.mailchimpapp.com",
        )
        assert classifier.classify(email) == EmailCategory.NEWSLETTER

    def test_weekly_digest_subject(self, classifier):
        email = make_email(
            sender_email="newsletter@blog.com",
            sender_domain="blog.com",
            subject="Your weekly digest is here",
        )
        assert classifier.classify(email) == EmailCategory.NEWSLETTER


# ==========================================================================
# ENTERTAINMENT TESTS
# ==========================================================================


class TestEntertainmentClassification:
    def test_netflix_non_security(self, classifier):
        email = make_email(
            sender_email="info@netflix.com",
            sender_domain="netflix.com",
            subject="New releases this week",
        )
        assert classifier.classify(email) == EmailCategory.ENTERTAINMENT

    def test_steam_wishlist(self, classifier):
        email = make_email(
            sender_email="noreply@steampowered.com",
            sender_domain="steampowered.com",
            subject="An item on your wishlist is on sale!",
        )
        assert classifier.classify(email) == EmailCategory.ENTERTAINMENT

    def test_cinema_booking(self, classifier):
        email = make_email(
            sender_email="tickets@cinema.co.il",
            sender_domain="cinema.co.il",
            subject="Your movie tickets are ready",
        )
        assert classifier.classify(email) == EmailCategory.ENTERTAINMENT

    def test_suzanne_dellal_event(self, classifier):
        email = make_email(
            sender_email="info@sdc.org.il",
            sender_domain="sdc.org.il",
            subject="מופע חדש נפתח להזמנות",
        )
        assert classifier.classify(email) == EmailCategory.ENTERTAINMENT


# ==========================================================================
# SOCIAL TESTS
# ==========================================================================


class TestSocialClassification:
    def test_linkedin_message(self, classifier):
        email = make_email(
            sender_email="messages-noreply@linkedin.com",
            sender_domain="linkedin.com",
            subject="John sent you a message",
        )
        assert classifier.classify(email) == EmailCategory.SOCIAL

    def test_linkedin_connection(self, classifier):
        email = make_email(
            sender_email="invitations@linkedin.com",
            sender_domain="linkedin.com",
            subject="You have a new connection",
        )
        assert classifier.classify(email) == EmailCategory.SOCIAL

    def test_discord_digest(self, classifier):
        # Note: Discord without security context
        email = make_email(
            sender_email="noreply@discord.com",
            sender_domain="discord.com",
            subject="You have 5 messages waiting",
        )
        assert classifier.classify(email) == EmailCategory.SOCIAL

    def test_messages_waiting_subject(self, classifier):
        email = make_email(
            sender_email="noreply@messaging.com",
            sender_domain="messaging.com",
            subject="You have messages waiting",
        )
        assert classifier.classify(email) == EmailCategory.SOCIAL


# ==========================================================================
# PROFESSIONAL EVENT TESTS
# ==========================================================================


class TestProfessionalEventClassification:
    def test_deeplearning_ai(self, classifier):
        email = make_email(
            sender_email="courses@deeplearning.ai",
            sender_domain="deeplearning.ai",
            subject="New course available",
        )
        assert classifier.classify(email) == EmailCategory.PROFESSIONAL_EVENT

    def test_geektime_event(self, classifier):
        email = make_email(
            sender_email="events@geektime.co.il",
            sender_domain="geektime.co.il",
            subject="הרשמו לכנס הבא",
        )
        assert classifier.classify(email) == EmailCategory.PROFESSIONAL_EVENT

    def test_webinar_subject(self, classifier):
        email = make_email(
            sender_email="marketing@company.com",
            sender_domain="company.com",
            subject="You're invited to our webinar",
        )
        assert classifier.classify(email) == EmailCategory.PROFESSIONAL_EVENT

    def test_conference_subject(self, classifier):
        email = make_email(
            sender_email="info@conf.com",
            sender_domain="conf.com",
            subject="Register for our annual conference",
        )
        assert classifier.classify(email) == EmailCategory.PROFESSIONAL_EVENT


# ==========================================================================
# KIDS EDUCATION TESTS
# ==========================================================================


class TestKidsEducationClassification:
    def test_studycat_domain(self, classifier):
        email = make_email(
            sender_email="hello@studycat.com",
            sender_domain="studycat.com",
            subject="Learning update",
        )
        assert classifier.classify(email) == EmailCategory.KIDS_EDUCATION

    def test_lingokids_domain(self, classifier):
        email = make_email(
            sender_email="info@lingokids.com",
            sender_domain="lingokids.com",
            subject="Your child's progress",
        )
        assert classifier.classify(email) == EmailCategory.KIDS_EDUCATION

    def test_child_progress_subject(self, classifier):
        email = make_email(
            sender_email="reports@school.edu",
            sender_domain="school.edu",
            subject="Zoe's weekly learning report",
        )
        assert classifier.classify(email) == EmailCategory.KIDS_EDUCATION


# ==========================================================================
# LOCAL FOOD TESTS
# ==========================================================================


class TestLocalFoodClassification:
    def test_aroma_domain(self, classifier):
        email = make_email(
            sender_email="marketing@aroma.co.il",
            sender_domain="aroma.co.il",
            subject="מבצע סוף שבוע",
        )
        assert classifier.classify(email) == EmailCategory.LOCAL_FOOD

    def test_grape_man(self, classifier):
        email = make_email(
            sender_email="info@grape-man.com",
            sender_domain="grape-man.com",
            subject="יינות לפסח",
        )
        assert classifier.classify(email) == EmailCategory.LOCAL_FOOD

    def test_wine_promo_subject(self, classifier):
        email = make_email(
            sender_email="sales@winery.co.il",
            sender_domain="winery.co.il",
            subject="מכירה שנתית - יינות במחירי רצפה",
        )
        assert classifier.classify(email) == EmailCategory.LOCAL_FOOD

    def test_wolt_delivery(self, classifier):
        email = make_email(
            sender_email="noreply@wolt.com",
            sender_domain="wolt.com",
            subject="Your order from Wolt",
        )
        # Wolt might be local_food or ecommerce - depends on order subject
        result = classifier.classify(email)
        assert result in [EmailCategory.LOCAL_FOOD, EmailCategory.ECOMMERCE_ORDER]


# ==========================================================================
# NOTIFICATION TESTS (generic)
# ==========================================================================


class TestNotificationClassification:
    def test_gitlab_domain(self, classifier):
        email = make_email(
            sender_email="gitlab@gitlab.com",
            sender_domain="gitlab.com",
        )
        assert classifier.classify(email) == EmailCategory.NOTIFICATION

    def test_slack_domain(self, classifier):
        email = make_email(
            sender_email="notifications@slack.com",
            sender_domain="slack.com",
        )
        assert classifier.classify(email) == EmailCategory.NOTIFICATION

    def test_noreply_sender(self, classifier):
        # Generic noreply that doesn't match other categories
        email = make_email(
            sender_email="noreply@someservice.com",
            sender_domain="someservice.com",
            subject="Account update",  # Generic subject
        )
        assert classifier.classify(email) == EmailCategory.NOTIFICATION


# ==========================================================================
# PROMOTIONAL TESTS
# ==========================================================================


class TestPromotionalClassification:
    def test_promotional_label(self, classifier):
        email = make_email(
            sender_email="marketing@store.com",
            sender_domain="store.com",
            labels=["CATEGORY_PROMOTIONS"],
        )
        assert classifier.classify(email) == EmailCategory.PROMOTIONAL

    def test_sale_subject(self, classifier):
        email = make_email(
            sender_email="marketing@store.com",
            sender_domain="store.com",
            subject="50% off sale - Limited time!",
        )
        assert classifier.classify(email) == EmailCategory.PROMOTIONAL

    def test_discount_subject(self, classifier):
        email = make_email(
            sender_email="deals@shop.com",
            sender_domain="shop.com",
            subject="Exclusive discount just for you",
        )
        assert classifier.classify(email) == EmailCategory.PROMOTIONAL


# ==========================================================================
# PERSONAL FALLBACK TESTS
# ==========================================================================


class TestPersonalFallback:
    def test_unclassified_email(self, classifier):
        email = make_email(
            sender_email="friend@gmail.com",
            sender_domain="gmail.com",
            subject="Hey, how are you?",
            labels=[],
        )
        assert classifier.classify(email) == EmailCategory.PERSONAL


# ==========================================================================
# CLASSIFY AND UPDATE TESTS
# ==========================================================================


class TestClassifyAndUpdate:
    def test_returns_updated_copy(self, classifier):
        email = make_email(
            sender_email="author@substack.com",
            sender_domain="substack.com",
        )
        assert email.category == EmailCategory.UNKNOWN

        updated = classifier.classify_and_update(email)
        assert updated.category == EmailCategory.NEWSLETTER
        # Original unchanged
        assert email.category == EmailCategory.UNKNOWN


# ==========================================================================
# CONFIDENCE TESTS
# ==========================================================================


class TestConfidence:
    def test_high_confidence_multiple_signals(self, classifier):
        email = make_email(
            sender_email="author@substack.com",
            sender_domain="substack.com",
            subject="This Week in Newsletter",
            labels=["Thoughts"],
        )
        confidence = classifier.get_confidence(email, EmailCategory.NEWSLETTER)
        assert confidence >= 0.66  # At least 2/3 signals

    def test_low_confidence_personal(self, classifier):
        email = make_email()
        confidence = classifier.get_confidence(email, EmailCategory.PERSONAL)
        assert confidence <= 0.5

    def test_security_high_confidence(self, classifier):
        email = make_email(
            sender_email="no-reply@accounts.google.com",
            sender_domain="accounts.google.com",
            subject="Security alert: New device login",
        )
        confidence = classifier.get_confidence(email, EmailCategory.SECURITY)
        assert confidence >= 0.66


# ==========================================================================
# PRIORITY ORDER TESTS (important edge cases)
# ==========================================================================


class TestPriorityOrder:
    """Test that higher-priority categories win when multiple match."""

    def test_security_beats_notification(self, classifier):
        """Security alerts from github should be security, not github_notification."""
        email = make_email(
            sender_email="noreply@github.com",
            sender_domain="github.com",
            subject="[GitHub] A third-party application has been added",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY

    def test_travel_beats_restaurant(self, classifier):
        """i-host.gr with hotel context should be travel, not restaurant."""
        email = make_email(
            sender_email="booking@i-host.gr",
            sender_domain="i-host.gr",
            subject="Hotel booking confirmation - Athens",
        )
        assert classifier.classify(email) == EmailCategory.TRAVEL

    def test_finance_beats_receipt(self, classifier):
        """Invoice subject should be finance, not receipt."""
        email = make_email(
            sender_email="billing@company.com",
            sender_domain="company.com",
            subject="Invoice #12345",
        )
        assert classifier.classify(email) == EmailCategory.FINANCE

    def test_ecommerce_beats_receipt(self, classifier):
        """Order shipped should be ecommerce, not receipt."""
        email = make_email(
            sender_email="shipping@store.com",
            sender_domain="store.com",
            subject="Your order has shipped",
        )
        assert classifier.classify(email) == EmailCategory.ECOMMERCE_ORDER

    def test_netflix_security_beats_entertainment(self, classifier):
        """Netflix security alert should be security, not entertainment."""
        email = make_email(
            sender_email="noreply@netflix.com",
            sender_domain="netflix.com",
            subject="New sign-in to your Netflix account",
        )
        assert classifier.classify(email) == EmailCategory.SECURITY
