"""
Security Audit Utilities for Shield Pro.
Provides forensic analysis tools for entropy calculation, network pattern recognition,
and supply chain typosquatting detection.
"""

import math
import re
from typing import List, Set, Optional


def calculate_shannon_entropy(data: str) -> float:
    """
    Calculates the Shannon entropy of a string.

    High entropy (> 4.5 for alphanumeric) often indicates encrypted or compressed
    payloads or obfuscated data.

    Args:
        data (str): The string to analyze.

    Returns:
        float: The calculated entropy value.
    """
    if not data:
        return 0.0

    entropy: float = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += -p_x * math.log(p_x, 2)

    return entropy


class NetworkForensics:
    """
    Heuristics for identifying suspicious network-related strings.
    """

    # IP v4 matcher (heuristic)
    IPV4_REGEX: re.Pattern = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )

    # URL matcher (more comprehensive for forensics)
    URL_REGEX: re.Pattern = re.compile(
        r"https?://(?:[-\w./?%&=@#]|(?:%[\da-fA-F]{2}))+"
    )

    @staticmethod
    def extract_ips(text: str) -> List[str]:
        """Extracts IPv4 addresses from text."""
        return NetworkForensics.IPV4_REGEX.findall(text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extracts URLs from text."""
        return NetworkForensics.URL_REGEX.findall(text)

    @staticmethod
    def check_link_safety(url: str) -> Optional[str]:
        """
        Analyzes a URL for suspicious phishing or exfiltration characteristics.

        Args:
            url (str): The URL to check.

        Returns:
            Optional[str]: A warning message if suspicious, else None.
        """
        url_lower = url.lower()

        # 1. IP Address Check
        domain_part = (
            url_lower.split("/")[2] if "//" in url_lower else url_lower.split("/")[0]
        )
        if re.match(r"^[\d.:]+$", domain_part):
            return f"Uses raw IP address: {domain_part}"

        # 2. Suspicious TLDs
        suspicious_tlds = {
            ".xyz",
            ".top",
            ".gq",
            ".ml",
            ".cf",
            ".tk",
            ".cn",
            ".ru",
            ".zip",
            ".mov",
        }
        if any(
            url_lower.endswith(tld) or f"{tld}/" in url_lower for tld in suspicious_tlds
        ):
            return f"Uses high-risk TLD: {url}"

        # 3. Phishing Keywords
        phishing_keywords = {
            "login",
            "signin",
            "verify",
            "update",
            "account",
            "secure",
            "banking",
        }
        if (
            any(kw in url_lower for kw in phishing_keywords)
            and "google.com" not in url_lower
            and "github.com" not in url_lower
        ):
            return f"Contains phishing keywords: {url}"

        return None


class SupplyChainForensics:
    """
    Forensics for detecting supply chain attacks like typosquatting.
    """

    # Subset of common trusted packages for detection
    WHITELIST: Set[str] = {
        "requests",
        "numpy",
        "pandas",
        "scipy",
        "flask",
        "django",
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "pytest",
        "mypy",
        "black",
        "flake8",
        "boto3",
        "google-cloud-storage",
        "azure-storage-blob",
        "pillow",
        "opencv-python",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "tensorflow",
        "torch",
        "keras",
        "nltk",
        "spacy",
        "beautifulsoup4",
        "lxml",
        "scrapy",
        "selenium",
        "playwright",
        "celery",
        "redis",
        "pymongo",
        "psycopg2",
        "mysql-connector-python",
        "pyyaml",
        "click",
        "typer",
        "tqdm",
        "rich",
        "loguru",
        "python-dotenv",
        "python-dateutil",
    }

    @staticmethod
    def check_typosquatting(package_name: str) -> Optional[str]:
        """
        Checks a package name against a whitelist for typosquatting.

        Args:
            package_name (str): The package name (may include versions).

        Returns:
            Optional[str]: The name of the authentic package if a squat is suspected.
        """
        pkg = package_name.lower().split("==")[0].split(">=")[0].strip()
        if pkg in SupplyChainForensics.WHITELIST:
            return None

        for real_pkg in SupplyChainForensics.WHITELIST:
            dist = SupplyChainForensics.levenshtein(pkg, real_pkg)
            if dist == 1 and len(pkg) > 3:
                return real_pkg
        return None

    @staticmethod
    def levenshtein(s1: str, s2: str) -> int:
        """Calculates Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return SupplyChainForensics.levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
