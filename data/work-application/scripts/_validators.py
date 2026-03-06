"""
_validators.py - CV formatting guardrails.
Port of js/validators.js. Stdlib only.

Validates character lengths, element counts, and full profile structure.

Usage:
    from _validators import validate_length, validate_count, validate_profile
    result = validate_length("Some text", "bullet")
    report = validate_profile(profile_dict)
"""

from datetime import datetime, date

# Character limits
LIMITS = {
    "line":            {"min": 0, "max": 90, "optimal": {"min": 50, "max": 75}},
    "bullet":          {"min": 0, "max": 150, "optimal": {"min": 80, "max": 120}},
    "jobTitle":        {"min": 10, "max": 60, "optimal": {"min": 30, "max": 50}},
    "companyName":     {"min": 5, "max": 50, "optimal": {"min": 20, "max": 40}},
    "summary":         {"min": 150, "max": 400, "optimal": {"min": 250, "max": 350}},
    "skillTag":        {"min": 3, "max": 25, "optimal": {"min": 8, "max": 15}},
    "wordsPerSentence": {"min": 8, "max": 25, "optimal": {"min": 14, "max": 20}},
}

# Quantity limits
COUNTS = {
    "bulletsPerExperience": {"min": 2, "max": 6, "optimal": {"min": 3, "max": 4}},
    "experiences":          {"min": 2, "max": 6, "optimal": {"min": 3, "max": 4}},
    "hardSkills":           {"min": 5, "max": 15, "optimal": {"min": 8, "max": 12}},
    "softSkills":           {"min": 3, "max": 8, "optimal": {"min": 4, "max": 6}},
    "summaryLines":         {"min": 3, "max": 6, "optimal": {"min": 4, "max": 5}},
}


def validate_length(text: str, type_: str) -> dict:
    """
    Validate a text string against character limits.
    Returns {valid: bool, status: str, message: str, length: int}
    """
    limit = LIMITS.get(type_)
    if not limit:
        return {"valid": True, "status": "unknown", "message": "Type inconnu", "length": len(text)}

    length = len(text)

    if length < limit["min"]:
        return {
            "valid": False,
            "status": "error",
            "message": f"Trop court ({length}/{limit['min']} min)",
            "length": length,
        }

    if length > limit["max"]:
        return {
            "valid": False,
            "status": "error",
            "message": f"Trop long ({length}/{limit['max']} max)",
            "length": length,
        }

    opt = limit["optimal"]
    if length < opt["min"] or length > opt["max"]:
        return {
            "valid": True,
            "status": "warning",
            "message": f"Acceptable mais hors optimal ({opt['min']}-{opt['max']})",
            "length": length,
        }

    return {"valid": True, "status": "valid", "message": "OK", "length": length}


def validate_count(count: int, type_: str) -> dict:
    """
    Validate a quantity against count limits.
    Returns {valid: bool, status: str, message: str, count: int}
    """
    limit = COUNTS.get(type_)
    if not limit:
        return {"valid": True, "status": "unknown", "message": "Type inconnu", "count": count}

    if count < limit["min"]:
        return {
            "valid": False,
            "status": "error",
            "message": f"Insuffisant ({count}/{limit['min']} min)",
            "count": count,
        }

    if count > limit["max"]:
        return {
            "valid": False,
            "status": "error",
            "message": f"Trop nombreux ({count}/{limit['max']} max)",
            "count": count,
        }

    opt = limit["optimal"]
    if count < opt["min"] or count > opt["max"]:
        return {
            "valid": True,
            "status": "warning",
            "message": f"Acceptable mais hors optimal ({opt['min']}-{opt['max']})",
            "count": count,
        }

    return {"valid": True, "status": "valid", "message": "OK", "count": count}


def validate_profile(profile: dict) -> dict:
    """
    Validate a complete profile.
    Returns {valid: bool, errors: list[str], warnings: list[str]}
    """
    errors = []
    warnings = []

    # Validate summary
    summary_text = (profile.get("summary") or {}).get("default", "")
    if summary_text:
        check = validate_length(summary_text, "summary")
        if check["status"] == "error":
            errors.append(f"Resume: {check['message']}")
        elif check["status"] == "warning":
            warnings.append(f"Resume: {check['message']}")

    # Validate hard skills
    hard_skills = profile.get("hard_skills") or []
    if hard_skills:
        check = validate_count(len(hard_skills), "hardSkills")
        if check["status"] == "error":
            errors.append(f"Competences techniques: {check['message']}")
        elif check["status"] == "warning":
            warnings.append(f"Competences techniques: {check['message']}")

        for skill in hard_skills:
            check = validate_length(skill.get("name", ""), "skillTag")
            if check["status"] == "error":
                errors.append(f'Competence "{skill["name"]}": {check["message"]}')

    # Validate soft skills
    soft_skills = profile.get("soft_skills") or []
    if soft_skills:
        check = validate_count(len(soft_skills), "softSkills")
        if check["status"] == "error":
            errors.append(f"Soft skills: {check['message']}")
        elif check["status"] == "warning":
            warnings.append(f"Soft skills: {check['message']}")

    # Validate experiences
    experiences = profile.get("experiences") or []
    if experiences:
        check = validate_count(len(experiences), "experiences")
        if check["status"] == "error":
            errors.append(f"Experiences: {check['message']}")
        elif check["status"] == "warning":
            warnings.append(f"Experiences: {check['message']}")

        for i, exp in enumerate(experiences, 1):
            # Job title
            title_check = validate_length(exp.get("title", ""), "jobTitle")
            if title_check["status"] == "error":
                errors.append(f"Experience {i} - Titre: {title_check['message']}")

            # Company name
            company_check = validate_length(exp.get("company", ""), "companyName")
            if company_check["status"] == "error":
                errors.append(f"Experience {i} - Entreprise: {company_check['message']}")

            # Achievements
            achievements = exp.get("achievements") or []
            if achievements:
                bullets_check = validate_count(len(achievements), "bulletsPerExperience")
                if bullets_check["status"] == "error":
                    errors.append(f"Experience {i} - Realisations: {bullets_check['message']}")
                elif bullets_check["status"] == "warning":
                    warnings.append(f"Experience {i} - Realisations: {bullets_check['message']}")

                for j, bullet in enumerate(achievements, 1):
                    bullet_check = validate_length(bullet, "bullet")
                    if bullet_check["status"] == "error":
                        errors.append(f"Experience {i} - Bullet {j}: {bullet_check['message']}")
                    elif bullet_check["status"] == "warning":
                        warnings.append(f"Experience {i} - Bullet {j}: {bullet_check['message']}")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def count_words(text: str) -> int:
    """Count words in a string."""
    return len([w for w in text.strip().split() if w])


def count_lines(text: str, chars_per_line: int = 75) -> int:
    """Estimate number of lines based on character count."""
    import math
    return math.ceil(len(text) / chars_per_line)


def format_date(date_str: str, lang: str = "fr") -> str:
    """
    Format a date string (YYYY-MM or 'present') for display.
    """
    if date_str == "present":
        return "Present" if lang == "en" else "Present"

    months_fr = ["Jan.", "Fev.", "Mars", "Avr.", "Mai", "Juin",
                 "Juil.", "Aout", "Sept.", "Oct.", "Nov.", "Dec."]
    months_en = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    parts = date_str.split("-")
    if len(parts) != 2:
        return date_str

    year = parts[0]
    month_idx = int(parts[1]) - 1
    months = months_en if lang == "en" else months_fr

    if 0 <= month_idx < 12:
        return f"{months[month_idx]} {year}"
    return date_str


def calculate_duration(start_date: str, end_date: str) -> str:
    """
    Calculate duration between two dates (YYYY-MM format).
    end_date can be 'present'.
    """
    start_parts = start_date.split("-")
    start_year, start_month = int(start_parts[0]), int(start_parts[1])

    if end_date == "present":
        now = date.today()
        end_year, end_month = now.year, now.month
    else:
        end_parts = end_date.split("-")
        end_year, end_month = int(end_parts[0]), int(end_parts[1])

    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    years = total_months // 12
    remaining = total_months % 12

    if years == 0:
        return f"{remaining} mois"
    elif remaining == 0:
        return f"{years} an{'s' if years > 1 else ''}"
    else:
        return f"{years} an{'s' if years > 1 else ''} {remaining} mois"


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text intelligently at word boundary."""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.8:
        return truncated[:last_space] + suffix
    return truncated + suffix
