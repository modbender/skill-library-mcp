"""Email classifier using heuristics (no LLM)."""

import re
from typing import Optional

from kaimail.models import EmailCategory, ParsedEmail


class EmailClassifier:
    """
    Classify emails into categories using rules and heuristics.

    No LLM involved - this is pure pattern matching.

    Priority order (highest to lowest):
    1. security - always flag security alerts
    2. travel - flights, hotels, cruises
    3. github_notification - GitHub CI/PR/issue
    4. restaurant_reservation - local restaurant bookings
    5. finance - invoices, billing, payments
    6. ecommerce_order - order confirmations/shipping
    7. health_insurance - medical/insurance
    8. receipt - payment confirmations (lower than finance/ecommerce)
    9. newsletter - Substack, known newsletters
    10. entertainment - streaming/gaming/events
    11. social - LinkedIn/Discord digests
    12. professional_event - conferences/webinars
    13. kids_education - kids apps/school
    14. local_food - food/restaurant promos
    15. notification - generic system notifications
    16. promotional - catch-all marketing
    17. personal - default fallback
    """

    # ==========================================================================
    # SECURITY patterns (highest priority)
    # ==========================================================================
    SECURITY_DOMAINS = [
        "accounts.google.com",
        "account.google.com",
    ]

    SECURITY_SENDERS = [
        r"no-reply@accounts\.google\.com",
        r"noreply@discord\.com",
        r"noreply@github\.com",
        r"noreply@netflix\.com",
        r"noreply@email\.apple\.com",
        r"security@",
        r"account-security@",
    ]

    SECURITY_SUBJECT_PATTERNS = [
        r"(?i)security alert",
        r"(?i)security notice",
        r"(?i)verification code",
        r"(?i)verify your",
        r"(?i)sign-?in code",
        r"(?i)new (device|sign-?in)",
        r"(?i)login from (new|a new)",
        r"(?i)oauth application",
        r"(?i)third-party.*(application|app).*(added|authorized)",
        r"(?i)account.*(access|data).*(attempt|request)",
        r"(?i)password (reset|changed)",
        r"(?i)suspicious activity",
        r"(?i)unusual sign-?in",
        r"(?i)2-?step verification",
        r"(?i)two-?factor",
    ]

    # ==========================================================================
    # TRAVEL patterns
    # ==========================================================================
    TRAVEL_DOMAINS = [
        "booking.com",
        "expedia.com",
        "hotels.com",
        "airbnb.com",
        "tripadvisor.com",
        "kayak.com",
        "skyscanner.com",
        "elal.com",
        "united.com",
        "delta.com",
        "aa.com",
        "southwest.com",
        "ryanair.com",
        "wizzair.com",
        "msc.com",  # MSC Cruises
    ]

    TRAVEL_SUBJECT_PATTERNS = [
        r"(?i)booking confirmation",
        r"(?i)flight confirmation",
        r"(?i)itinerary",
        r"(?i)your trip",
        r"(?i)hotel confirmation",
        r"(?i)check-?in (details|instructions|reminder)",
        r"(?i)boarding pass",
        r"(?i)cruise",
        r"(?i)טיסה",  # Hebrew: flight
        r"(?i)מלון",  # Hebrew: hotel
    ]

    # ==========================================================================
    # GITHUB NOTIFICATION patterns
    # ==========================================================================
    GITHUB_DOMAINS = [
        "github.com",
    ]

    GITHUB_SENDERS = [
        r"notifications@github\.com",
        r"noreply@github\.com",
    ]

    GITHUB_SUBJECT_PATTERNS = [
        r"\[[\w\-]+/[\w\-]+\]",  # [owner/repo] prefix
        r"(?i)run (failed|succeeded|cancelled)",
        r"(?i)pull request",
        r"(?i)issue (opened|closed|reopened)",
        r"(?i)merged .* into",
        r"(?i)pushed to",
        r"(?i)workflow run",
    ]

    # ==========================================================================
    # RESTAURANT RESERVATION patterns (local, not travel)
    # ==========================================================================
    RESTAURANT_DOMAINS = [
        "tabit.cloud",
        "opentable.com",
        "resy.com",
        "yelp.com",
        "rest.co.il",
        "i-host.gr",  # Greek restaurants
    ]

    RESTAURANT_SUBJECT_PATTERNS = [
        r"(?i)אשרו את הזמנתכם",  # Hebrew: confirm your reservation
        r"(?i)reservation confirmation",
        r"(?i)reservation.*(kind )?reminder",
        r"(?i)your table",
        r"(?i)booking at",
        r"(?i)reservation for",
        r"(?i)your reservation at",
    ]

    # ==========================================================================
    # FINANCE patterns
    # ==========================================================================
    FINANCE_DOMAINS = [
        "1password.com",
        "ravpass.co.il",
        "payoneer.com",
        "wise.com",
        "revolut.com",
    ]

    FINANCE_SUBJECT_PATTERNS = [
        r"(?i)\binvoice\b",
        r"(?i)חשבונית",  # Hebrew: invoice
        r"(?i)חיוב",  # Hebrew: charge
        r"(?i)your receipt",
        r"(?i)\bpayment\b",
        r"(?i)subscription",
        r"(?i)עסקה",  # Hebrew: transaction
        r"(?i)updating the cost",
        r"(?i)billing",
        r"(?i)monthly statement",
    ]

    # ==========================================================================
    # ECOMMERCE ORDER patterns
    # ==========================================================================
    ECOMMERCE_DOMAINS = [
        "ksp.co.il",
        "iherb.com",
        "amazon.com",
        "bikes4kids",
        "aliexpress.com",
        "ebay.com",
        "etsy.com",
    ]

    ECOMMERCE_SUBJECT_PATTERNS = [
        r"(?i)הזמנה מספר",  # Hebrew: order number
        r"(?i)אישור הזמנה",  # Hebrew: order confirmation
        r"(?i)order.*(shipped|dispatched)",  # "order has shipped", "order shipped"
        r"(?i)order confirmation",
        r"(?i)shipping (delay|update|notification)",
        r"(?i)your.*order",  # "your order", "your Amazon order"
        r"(?i)delivery (update|scheduled|confirmed)",
        r"(?i)track(ing)? (your|number|update)",
        r"(?i)out for delivery",
        r"(?i)package (delivered|shipped)",
        r"(?i)has shipped",  # Generic shipped pattern
    ]

    # ==========================================================================
    # HEALTH/INSURANCE patterns
    # ==========================================================================
    HEALTH_DOMAINS = [
        "fnx.co.il",  # Phoenix Insurance
        "meuhedet.co.il",
        "clalit.co.il",
        "maccabi.co.il",
        "leumit.co.il",
    ]

    HEALTH_SUBJECT_PATTERNS = [
        r"(?i)פוליסת בריאות",  # Hebrew: health policy
        r"(?i)מרפאה",  # Hebrew: clinic
        r"(?i)חידוש",  # Hebrew: renewal
        r"(?i)health insurance",
        r"(?i)medical",
        r"(?i)\bמאוחדת\b",  # Meuhedet HMO (word boundary to avoid false positives)
        r"(?i)\bמכבי\b",  # Maccabi HMO
        r"(?i)\bכללית\b",  # Clalit HMO
        r"(?i)^לאומית\b",  # Leumit HMO - require start of word, avoid בינלאומית
        r"(?i)appointment (confirmation|reminder)",
        r"(?i)prescription",
        r"(?i)תור",  # Hebrew: appointment
    ]

    # ==========================================================================
    # RECEIPT patterns (payment confirmations - lower priority than finance)
    # ==========================================================================
    RECEIPT_DOMAINS = [
        "apple.com",
        "email.apple.com",
        "google.com",
        "paypal.com",
        "stripe.com",
        "amazon.com",
    ]

    RECEIPT_SUBJECT_PATTERNS = [
        r"(?i)your (order|purchase)",
        r"(?i)payment (confirmation|received)",
        r"(?i)subscription renew",
        r"(?i)receipt from",
        r"(?i)^receipt",  # Subject starting with "Receipt"
        r"(?i)receipt for",  # "Receipt for your payment"
        r"(?i)thank you for your (order|purchase)",
    ]

    # ==========================================================================
    # NEWSLETTER patterns
    # ==========================================================================
    NEWSLETTER_DOMAINS = [
        "substack.com",
        "substackcdn.com",
        "beehiiv.com",
        "buttondown.email",
        "mailchimp.com",
        "mailchimpapp.com",
        "convertkit.com",
        "ghost.io",
        "revue.email",
        "getrevue.co",
        "stratechery.com",
        "ben-evans.com",
    ]

    NEWSLETTER_SENDER_PATTERNS = [
        r"newsletter",
        r"digest",
        r"weekly",
        r"daily",
        r"update",
        r"from .+ substack",
    ]

    NEWSLETTER_SUBJECT_PATTERNS = [
        r"(?i)this week in",
        r"(?i)weekly digest",
        r"(?i)daily digest",
        r"(?i)newsletter",
    ]

    # ==========================================================================
    # ENTERTAINMENT patterns
    # ==========================================================================
    ENTERTAINMENT_DOMAINS = [
        "netflix.com",
        "cinema.co.il",
        "steampowered.com",
        "store.steampowered.com",
        "sdc.org.il",  # Suzanne Dellal
        "ourjazzproject",
        "spotify.com",
        "disney.com",
        "hulu.com",
        "primevideo.com",
        "hbomax.com",
        "yes.co.il",
    ]

    ENTERTAINMENT_SUBJECT_PATTERNS = [
        r"(?i)wishlist",
        r"(?i)download is ready",
        r"(?i)נפתח",  # Hebrew: opened/started (events)
        r"(?i)new release",
        r"(?i)now available",
        r"(?i)stream",
        r"(?i)watch now",
    ]

    # ==========================================================================
    # SOCIAL patterns
    # ==========================================================================
    SOCIAL_DOMAINS = [
        "linkedin.com",
        "facebookmail.com",
        "twitter.com",
        "x.com",
        "instagram.com",
    ]

    SOCIAL_SENDERS = [
        r".*@linkedin\.com",
        r".*@discord\.com",
    ]

    SOCIAL_SUBJECT_PATTERNS = [
        r"(?i)sent you a message",
        r"(?i)messages waiting",
        r"(?i)\bdigest\b",
        r"(?i)new connection",
        r"(?i)accepted your",
        r"(?i)viewed your profile",
        r"(?i)mentioned you",
        r"(?i)replied to",
    ]

    # ==========================================================================
    # PROFESSIONAL EVENT patterns
    # ==========================================================================
    PROFESSIONAL_EVENT_DOMAINS = [
        "deeplearning.ai",
        "geektime.co.il",
        "headstart.co.il",
        "eventbrite.com",
        "meetup.com",
        "zoom.us",
        "webinar.net",
    ]

    PROFESSIONAL_EVENT_SUBJECT_PATTERNS = [
        r"(?i)webinar",
        r"(?i)conference",
        r"(?i)\binvited\b",
        r"(?i)הרצאה",  # Hebrew: lecture
        r"(?i)אירוע",  # Hebrew: event
        r"(?i)register now",
        r"(?i)join us",
        r"(?i)upcoming event",
        r"(?i)summit",
        r"(?i)workshop",
    ]

    # ==========================================================================
    # KIDS EDUCATION patterns
    # ==========================================================================
    KIDS_EDUCATION_DOMAINS = [
        "studycat.com",
        "lingokids.com",
        "abcmouse.com",
        "khanacademy.org",
        "duolingo.com",
    ]

    KIDS_EDUCATION_SUBJECT_PATTERNS = [
        r"(?i)(zoe|lenny).*(progress|learning|achievement)",
        r"(?i)child.*(learning|progress)",
        r"(?i)weekly (learning )?report",
        r"(?i)educational",
    ]

    # ==========================================================================
    # LOCAL FOOD patterns (Israeli food promos)
    # ==========================================================================
    LOCAL_FOOD_DOMAINS = [
        "aroma.co.il",
        "manovino.co.il",
        "delicatessen",
        "sipurpashut.com",
        "grape-man.com",
        "margalit-winery.com",
        "wolt.com",
        "10bis.co.il",
    ]

    LOCAL_FOOD_SUBJECT_PATTERNS = [
        r"(?i)ארומה.*הזמנה",  # Aroma order
        r"(?i)הזמנה לסוף השבוע",  # Hebrew: weekend order
        r"(?i)פסח",  # Hebrew: Passover
        r"(?i)מכירה שנתית",  # Hebrew: annual sale
        r"(?i)תפריט",  # Hebrew: menu
        r"(?i)wine.*sale",
        r"(?i)יין",  # Hebrew: wine
    ]

    # ==========================================================================
    # NOTIFICATION patterns (generic)
    # ==========================================================================
    NOTIFICATION_DOMAINS = [
        "gitlab.com",
        "bitbucket.org",
        "slack.com",
        "trello.com",
        "asana.com",
        "jira.atlassian.com",
        "notion.so",
        "linear.app",
        "vercel.com",
        "netlify.com",
        "aws.amazon.com",
    ]

    NOTIFICATION_SENDER_PATTERNS = [
        r"noreply@",
        r"no-reply@",
        r"no_reply@",
        r"notifications?@",
        r"alerts?@",
        r"support@",
        r"account.*@",
    ]

    # ==========================================================================
    # PROMOTIONAL patterns (catch-all marketing)
    # ==========================================================================
    PROMOTIONAL_LABELS = [
        "CATEGORY_PROMOTIONS",
    ]

    PROMOTIONAL_SUBJECT_PATTERNS = [
        r"(?i)\d+%\s*off",
        r"(?i)\bsale\b",
        r"(?i)\bdeal\b",
        r"(?i)limited time",
        r"(?i)special offer",
        r"(?i)discount",
        r"(?i)free shipping",
        r"(?i)don'?t miss",
        r"(?i)exclusive",
        r"(?i)last chance",
    ]

    def classify(self, email: ParsedEmail) -> EmailCategory:
        """
        Classify an email into a category.

        Priority order (highest to lowest - see class docstring).
        """
        # 1. Security (highest priority)
        if self._is_security(email):
            return EmailCategory.SECURITY

        # 2. Travel
        if self._is_travel(email):
            return EmailCategory.TRAVEL

        # 3. GitHub notifications
        if self._is_github_notification(email):
            return EmailCategory.GITHUB_NOTIFICATION

        # 4. Restaurant reservations (local, not travel)
        if self._is_restaurant_reservation(email):
            return EmailCategory.RESTAURANT_RESERVATION

        # 5. Finance
        if self._is_finance(email):
            return EmailCategory.FINANCE

        # 6. Ecommerce orders
        if self._is_ecommerce_order(email):
            return EmailCategory.ECOMMERCE_ORDER

        # 7. Health/Insurance
        if self._is_health_insurance(email):
            return EmailCategory.HEALTH_INSURANCE

        # 8. Receipt (payment confirmation)
        if self._is_receipt(email):
            return EmailCategory.RECEIPT

        # 9. Newsletter
        if self._is_newsletter(email):
            return EmailCategory.NEWSLETTER

        # 10. Entertainment
        if self._is_entertainment(email):
            return EmailCategory.ENTERTAINMENT

        # 11. Social
        if self._is_social(email):
            return EmailCategory.SOCIAL

        # 12. Professional events
        if self._is_professional_event(email):
            return EmailCategory.PROFESSIONAL_EVENT

        # 13. Kids education
        if self._is_kids_education(email):
            return EmailCategory.KIDS_EDUCATION

        # 14. Local food
        if self._is_local_food(email):
            return EmailCategory.LOCAL_FOOD

        # 15. Generic notification
        if self._is_notification(email):
            return EmailCategory.NOTIFICATION

        # 16. Promotional
        if self._is_promotional(email):
            return EmailCategory.PROMOTIONAL

        # 17. Default: personal
        return EmailCategory.PERSONAL

    def classify_and_update(self, email: ParsedEmail) -> ParsedEmail:
        """Classify email and return a copy with category set."""
        category = self.classify(email)
        return email.model_copy(update={"category": category})

    # ==========================================================================
    # Classification methods
    # ==========================================================================

    def _is_security(self, email: ParsedEmail) -> bool:
        """Check if email is a security alert."""
        # Check specific security domains
        if any(domain in email.sender_email for domain in self.SECURITY_DOMAINS):
            return True

        # Check security sender patterns
        if any(re.search(p, email.sender_email, re.IGNORECASE) for p in self.SECURITY_SENDERS):
            # Also check subject for security context
            if any(re.search(p, email.subject) for p in self.SECURITY_SUBJECT_PATTERNS):
                return True

        # Check subject patterns alone (strong indicators)
        strong_security_patterns = [
            r"(?i)security alert",
            r"(?i)verification code",
            r"(?i)sign-?in code",
            r"(?i)new device",
            r"(?i)suspicious activity",
            r"(?i)third-party.*(application|app).*(added|authorized)",
        ]
        if any(re.search(p, email.subject) for p in strong_security_patterns):
            return True

        return False

    def _is_travel(self, email: ParsedEmail) -> bool:
        """Check if email is travel-related."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.TRAVEL_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.TRAVEL_SUBJECT_PATTERNS):
            return True

        # Check for "Travel" label
        if "Travel" in email.labels:
            return True

        # i-host.gr with travel context (not just restaurant)
        if "i-host.gr" in email.sender_domain:
            travel_context = [r"(?i)flight", r"(?i)hotel", r"(?i)cruise", r"(?i)itinerary"]
            if any(re.search(p, email.subject) for p in travel_context):
                return True

        return False

    def _is_github_notification(self, email: ParsedEmail) -> bool:
        """Check if email is a GitHub notification."""
        # Check sender
        if any(re.search(p, email.sender_email, re.IGNORECASE) for p in self.GITHUB_SENDERS):
            return True

        # Check domain + GitHub label
        if "github.com" in email.sender_domain:
            return True

        # Check GitHub label
        if "GitHub" in email.labels:
            return True

        return False

    def _is_restaurant_reservation(self, email: ParsedEmail) -> bool:
        """Check if email is a local restaurant reservation."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.RESTAURANT_DOMAINS):
            # For i-host.gr, only match if NOT travel context
            if "i-host.gr" in email.sender_domain:
                travel_context = [r"(?i)flight", r"(?i)hotel", r"(?i)cruise"]
                if any(re.search(p, email.subject) for p in travel_context):
                    return False
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.RESTAURANT_SUBJECT_PATTERNS):
            return True

        return False

    def _is_finance(self, email: ParsedEmail) -> bool:
        """Check if email is finance-related (invoices, billing, payments)."""
        # Exclude if it's clearly a receipt (explicit "receipt" in subject)
        receipt_override = [r"(?i)\breceipt\b", r"(?i)your receipt"]
        if any(re.search(p, email.subject) for p in receipt_override):
            return False

        # Check domain
        if any(domain in email.sender_domain for domain in self.FINANCE_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.FINANCE_SUBJECT_PATTERNS):
            # Exclude if it's clearly ecommerce order
            ecommerce_override = [r"(?i)order.*shipped", r"(?i)הזמנה מספר", r"(?i)out for delivery"]
            if not any(re.search(p, email.subject) for p in ecommerce_override):
                return True

        return False

    def _is_ecommerce_order(self, email: ParsedEmail) -> bool:
        """Check if email is an ecommerce order/shipping notification."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.ECOMMERCE_DOMAINS):
            # Check for order-related subject
            if any(re.search(p, email.subject) for p in self.ECOMMERCE_SUBJECT_PATTERNS):
                return True

        # Check subject patterns alone
        if any(re.search(p, email.subject) for p in self.ECOMMERCE_SUBJECT_PATTERNS):
            return True

        return False

    def _is_health_insurance(self, email: ParsedEmail) -> bool:
        """Check if email is health/insurance related."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.HEALTH_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.HEALTH_SUBJECT_PATTERNS):
            return True

        return False

    def _is_receipt(self, email: ParsedEmail) -> bool:
        """Check if email is a receipt/invoice."""
        # Check domain + subject
        if any(domain in email.sender_domain for domain in self.RECEIPT_DOMAINS):
            if any(re.search(p, email.subject) for p in self.RECEIPT_SUBJECT_PATTERNS):
                return True
            # Apple invoice special case
            if "apple.com" in email.sender_domain and "invoice" in email.subject.lower():
                return True

        # Check subject patterns alone
        if any(re.search(p, email.subject) for p in self.RECEIPT_SUBJECT_PATTERNS):
            return True

        return False

    def _is_newsletter(self, email: ParsedEmail) -> bool:
        """Check if email is a newsletter."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.NEWSLETTER_DOMAINS):
            return True

        # Check sender patterns
        sender_lower = email.sender_email.lower()
        if any(re.search(p, sender_lower) for p in self.NEWSLETTER_SENDER_PATTERNS):
            return True

        # Check subject patterns
        if any(
            re.search(p, email.subject, re.IGNORECASE) for p in self.NEWSLETTER_SUBJECT_PATTERNS
        ):
            return True

        # Check for "Thoughts" label (user's newsletter label)
        if "Thoughts" in email.labels:
            return True

        return False

    def _is_entertainment(self, email: ParsedEmail) -> bool:
        """Check if email is entertainment-related."""
        # Check domain (but not netflix security emails)
        if any(domain in email.sender_domain for domain in self.ENTERTAINMENT_DOMAINS):
            # Exclude security alerts
            if not any(re.search(p, email.subject) for p in self.SECURITY_SUBJECT_PATTERNS):
                return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.ENTERTAINMENT_SUBJECT_PATTERNS):
            return True

        return False

    def _is_social(self, email: ParsedEmail) -> bool:
        """Check if email is from social platforms."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.SOCIAL_DOMAINS):
            return True

        # Check sender patterns (but not security)
        if any(re.search(p, email.sender_email, re.IGNORECASE) for p in self.SOCIAL_SENDERS):
            # Exclude security alerts
            if not any(re.search(p, email.subject) for p in self.SECURITY_SUBJECT_PATTERNS):
                return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.SOCIAL_SUBJECT_PATTERNS):
            return True

        return False

    def _is_professional_event(self, email: ParsedEmail) -> bool:
        """Check if email is about professional events."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.PROFESSIONAL_EVENT_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.PROFESSIONAL_EVENT_SUBJECT_PATTERNS):
            return True

        return False

    def _is_kids_education(self, email: ParsedEmail) -> bool:
        """Check if email is kids education related."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.KIDS_EDUCATION_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.KIDS_EDUCATION_SUBJECT_PATTERNS):
            return True

        return False

    def _is_local_food(self, email: ParsedEmail) -> bool:
        """Check if email is local food/restaurant promos."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.LOCAL_FOOD_DOMAINS):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.LOCAL_FOOD_SUBJECT_PATTERNS):
            return True

        return False

    def _is_notification(self, email: ParsedEmail) -> bool:
        """Check if email is a generic system notification."""
        # Check domain
        if any(domain in email.sender_domain for domain in self.NOTIFICATION_DOMAINS):
            return True

        # Check sender patterns
        if any(
            re.search(p, email.sender_email, re.IGNORECASE)
            for p in self.NOTIFICATION_SENDER_PATTERNS
        ):
            return True

        return False

    def _is_promotional(self, email: ParsedEmail) -> bool:
        """Check if email is promotional."""
        # Check Gmail promotional label
        if any(label in self.PROMOTIONAL_LABELS for label in email.labels):
            return True

        # Check subject patterns
        if any(re.search(p, email.subject) for p in self.PROMOTIONAL_SUBJECT_PATTERNS):
            return True

        return False

    def get_confidence(self, email: ParsedEmail, category: Optional[EmailCategory] = None) -> float:
        """
        Get classification confidence (0.0 - 1.0).

        Higher confidence when multiple signals match.
        """
        if category is None:
            category = self.classify(email)

        signals = 0
        max_signals = 3  # Domain, subject pattern, label

        if category == EmailCategory.SECURITY:
            if any(d in email.sender_email for d in self.SECURITY_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.SECURITY_SUBJECT_PATTERNS):
                signals += 1
            if any(re.search(p, email.sender_email, re.IGNORECASE) for p in self.SECURITY_SENDERS):
                signals += 1

        elif category == EmailCategory.TRAVEL:
            if any(d in email.sender_domain for d in self.TRAVEL_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.TRAVEL_SUBJECT_PATTERNS):
                signals += 1
            if "Travel" in email.labels:
                signals += 1

        elif category == EmailCategory.GITHUB_NOTIFICATION:
            if "github.com" in email.sender_domain:
                signals += 1
            if any(re.search(p, email.subject) for p in self.GITHUB_SUBJECT_PATTERNS):
                signals += 1
            if "GitHub" in email.labels:
                signals += 1

        elif category == EmailCategory.RESTAURANT_RESERVATION:
            if any(d in email.sender_domain for d in self.RESTAURANT_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.RESTAURANT_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.FINANCE:
            if any(d in email.sender_domain for d in self.FINANCE_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.FINANCE_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.ECOMMERCE_ORDER:
            if any(d in email.sender_domain for d in self.ECOMMERCE_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.ECOMMERCE_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.HEALTH_INSURANCE:
            if any(d in email.sender_domain for d in self.HEALTH_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.HEALTH_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.RECEIPT:
            if any(d in email.sender_domain for d in self.RECEIPT_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.RECEIPT_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.NEWSLETTER:
            if any(d in email.sender_domain for d in self.NEWSLETTER_DOMAINS):
                signals += 1
            if any(
                re.search(p, email.subject, re.IGNORECASE) for p in self.NEWSLETTER_SUBJECT_PATTERNS
            ):
                signals += 1
            if "Thoughts" in email.labels or "CATEGORY_UPDATES" in email.labels:
                signals += 1

        elif category == EmailCategory.ENTERTAINMENT:
            if any(d in email.sender_domain for d in self.ENTERTAINMENT_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.ENTERTAINMENT_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.SOCIAL:
            if any(d in email.sender_domain for d in self.SOCIAL_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.SOCIAL_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.PROFESSIONAL_EVENT:
            if any(d in email.sender_domain for d in self.PROFESSIONAL_EVENT_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.PROFESSIONAL_EVENT_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.KIDS_EDUCATION:
            if any(d in email.sender_domain for d in self.KIDS_EDUCATION_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.KIDS_EDUCATION_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.LOCAL_FOOD:
            if any(d in email.sender_domain for d in self.LOCAL_FOOD_DOMAINS):
                signals += 1
            if any(re.search(p, email.subject) for p in self.LOCAL_FOOD_SUBJECT_PATTERNS):
                signals += 1

        elif category == EmailCategory.NOTIFICATION:
            if any(d in email.sender_domain for d in self.NOTIFICATION_DOMAINS):
                signals += 1
            if any(
                re.search(p, email.sender_email, re.IGNORECASE)
                for p in self.NOTIFICATION_SENDER_PATTERNS
            ):
                signals += 1

        elif category == EmailCategory.PROMOTIONAL:
            if any(lbl in self.PROMOTIONAL_LABELS for lbl in email.labels):
                signals += 1
            if any(re.search(p, email.subject) for p in self.PROMOTIONAL_SUBJECT_PATTERNS):
                signals += 1

        # Personal has low confidence by default (it's the fallback)
        if category == EmailCategory.PERSONAL:
            return 0.3

        return min(1.0, (signals + 1) / max_signals)
