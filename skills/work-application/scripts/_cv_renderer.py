"""
_cv_renderer.py - HTML CV generation for the work-application skill.
Generates standalone HTML files with embedded CSS. Stdlib only.
Ports the rendering logic from js/app.js and print.html.
"""

import html
from datetime import date

from _cv_styles import get_full_css
from _validators import format_date

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------

I18N = {
    "fr": {
        "profile": "Profil",
        "skills": "Competences",
        "experience": "Experience Professionnelle",
        "education": "Formation",
        "certifications": "Certifications",
        "languages": "Langues",
        "projects": "Projets",
        "qualities": "Qualites",
        "contact": "Contact",
        "about": "A propos",
        "career": "Parcours",
        "present": "Present",
    },
    "en": {
        "profile": "Profile",
        "skills": "Skills",
        "experience": "Professional Experience",
        "education": "Education",
        "certifications": "Certifications",
        "languages": "Languages",
        "projects": "Projects",
        "qualities": "Soft Skills",
        "contact": "Contact",
        "about": "About",
        "career": "Career",
        "present": "Present",
    },
}

# ---------------------------------------------------------------------------
# Default sections visibility
# ---------------------------------------------------------------------------

DEFAULT_SECTIONS = {
    "summary": True,
    "skills": True,
    "experience": True,
    "education": True,
    "certifications": True,
    "languages": True,
    "projects": False,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _t(key: str, lang: str) -> str:
    """Translation lookup."""
    return I18N.get(lang, I18N["fr"]).get(key, key)


def _format_date(date_str: str, lang: str) -> str:
    """Format YYYY-MM or 'present' to display string."""
    if not date_str:
        return ""
    if date_str.lower() == "present":
        return _t("present", lang)
    return format_date(date_str, lang)


def _esc(text) -> str:
    """HTML-escape user-provided text."""
    if text is None:
        return ""
    return html.escape(str(text))


def _linkedin_short(url: str) -> str:
    """Extract 'linkedin.com/in/username' from a full LinkedIn URL."""
    if not url:
        return ""
    url_clean = url.rstrip("/")
    # Remove protocol
    for prefix in ("https://", "http://", "www."):
        if url_clean.startswith(prefix):
            url_clean = url_clean[len(prefix):]
    # Remove www. if still present after protocol strip
    if url_clean.startswith("www."):
        url_clean = url_clean[4:]
    return url_clean


# ---------------------------------------------------------------------------
# Shared helper renderers
# ---------------------------------------------------------------------------


def _render_skills_by_category(skills: list, highlight_names: list = None) -> str:
    """Group skills by category and render.

    If all skills share one category (or none), render as a flat list.
    Otherwise group by category with category headers.
    """
    if not skills:
        return ""

    if highlight_names is None:
        highlight_names = []
    highlight_set = {n.lower() for n in highlight_names}

    # Group by category
    categories = {}
    for s in skills:
        cat = s.get("category", "")
        categories.setdefault(cat, []).append(s)

    # Single category or no category -> flat list
    if len(categories) <= 1:
        parts = []
        for s in skills:
            name = _esc(s.get("name", ""))
            cls = "cv-skill-tag"
            if name.lower() in highlight_set or s.get("highlight"):
                cls += " highlight"
            parts.append(f'<span class="{cls}">{name}</span>')
        return f'<div class="cv-skills-list">{"".join(parts)}</div>'

    # Multiple categories
    lines = []
    for cat, cat_skills in categories.items():
        tags = []
        for s in cat_skills:
            name = _esc(s.get("name", ""))
            cls = "cv-skill-tag"
            if name.lower() in highlight_set or s.get("highlight"):
                cls += " highlight"
            tags.append(f'<span class="{cls}">{name}</span>')
        cat_label = _esc(cat) if cat else ""
        lines.append(
            f'<div class="cv-skills-category">'
            f'<span class="cv-skills-category-name">{cat_label}</span>'
            f'<div class="cv-skills-list">{"".join(tags)}</div>'
            f'</div>'
        )
    return "".join(lines)


def _render_experience(exp: dict, lang: str) -> str:
    """Render a single experience item with cssClass support."""
    title = _esc(exp.get("title", ""))
    company = _esc(exp.get("company", ""))
    location = _esc(exp.get("location", ""))
    description = _esc(exp.get("description", ""))
    start = _format_date(exp.get("startDate", ""), lang)
    end = _format_date(exp.get("endDate", ""), lang)
    date_range = f"{start} - {end}" if start else end
    css_class = exp.get("cssClass", "")
    extra_cls = f" {_esc(css_class)}" if css_class else ""

    h = f'<div class="cv-experience-item{extra_cls}">'
    h += '<div class="cv-experience-header">'
    h += f'<span class="cv-experience-title">{title}</span>'
    h += f'<span class="cv-experience-date">{_esc(date_range)}</span>'
    h += '</div>'

    company_html = company
    if location:
        company_html += f' <span class="cv-experience-location">- {location}</span>'
    h += f'<div class="cv-experience-company">{company_html}</div>'

    if description:
        h += f'<div class="cv-experience-description">{description}</div>'

    achievements = exp.get("achievements") or []
    if achievements:
        h += '<ul class="cv-experience-achievements">'
        for a in achievements:
            h += f"<li>{_esc(a)}</li>"
        h += "</ul>"

    h += "</div>"
    return h


def _render_experience_creative(exp: dict, lang: str) -> str:
    """Render a single experience item for the creative (timeline) template."""
    title = _esc(exp.get("title", ""))
    company = _esc(exp.get("company", ""))
    location = _esc(exp.get("location", ""))
    description = _esc(exp.get("description", ""))
    start = _format_date(exp.get("startDate", ""), lang)
    end = _format_date(exp.get("endDate", ""), lang)
    date_range = f"{start} - {end}" if start else end

    h = '<div class="cv-experience-item">'
    h += '<div class="cv-experience-header">'
    h += f'<span class="cv-experience-title">{title}</span>'
    h += '</div>'
    h += '<div class="cv-experience-meta">'
    company_html = company
    if location:
        company_html += f' <span class="cv-experience-location">- {location}</span>'
    h += f'<span class="cv-experience-company">{company_html}</span>'
    h += f'<span class="cv-experience-date">{_esc(date_range)}</span>'
    h += '</div>'

    if description:
        h += f'<div class="cv-experience-description">{description}</div>'

    achievements = exp.get("achievements") or []
    if achievements:
        h += '<ul class="cv-experience-achievements">'
        for a in achievements:
            h += f"<li>{_esc(a)}</li>"
        h += "</ul>"

    h += "</div>"
    return h


def _render_education_classic(edu: dict) -> str:
    """Render a single education item: degree - field, institution, year."""
    degree = _esc(edu.get("degree", ""))
    field = _esc(edu.get("field", ""))
    institution = _esc(edu.get("institution", ""))
    year = _esc(str(edu.get("year", "")))
    honors = _esc(edu.get("honors", ""))

    title = degree
    if field:
        title += f" - {field}" if title else field

    h = '<div class="cv-education-item">'
    h += '<div class="cv-education-header">'
    h += f'<span class="cv-education-degree">{title}</span>'
    h += f'<span class="cv-education-year">{year}</span>'
    h += '</div>'
    if institution:
        h += f'<div class="cv-education-institution">{institution}</div>'
    if honors:
        h += f'<div class="cv-education-honors">{honors}</div>'
    h += '</div>'
    return h


def _section_visible(sections: dict, key: str) -> bool:
    """Check if a section should be rendered."""
    return sections.get(key, False)


def _hidden_cls(sections: dict, key: str) -> str:
    """Return ' hidden' class suffix if the section is not visible."""
    return "" if _section_visible(sections, key) else " hidden"


# ---------------------------------------------------------------------------
# Contact helpers
# ---------------------------------------------------------------------------


def _build_contact_items(p: dict) -> list:
    """Build a list of contact dicts: {text, href?, icon?}."""
    items = []
    email = p.get("email", "")
    phone = p.get("phone", "")
    location = p.get("location", "")
    linkedin = p.get("linkedin", "")
    website = p.get("website", "")
    github = p.get("github", "")

    if email:
        items.append({"text": email, "href": f"mailto:{email}", "icon": "\u2709"})
    if phone:
        items.append({"text": phone, "icon": "\u260E"})
    if location:
        items.append({"text": location, "icon": "\u2302"})
    if linkedin:
        short = _linkedin_short(linkedin)
        items.append({"text": short, "href": linkedin, "icon": "in"})
    if website:
        items.append({"text": website, "href": website, "icon": "\u2B50"})
    if github:
        items.append({"text": github, "href": github, "icon": "\u2318"})

    return items


def _render_contact_inline(items: list) -> str:
    """Render contact items inline (for classic header)."""
    parts = []
    for item in items:
        text = _esc(item["text"])
        if item.get("href"):
            href = _esc(item["href"])
            short = _esc(item["text"])
            parts.append(
                f'<span class="cv-contact-item">'
                f'<a href="{href}" data-short-url="{short}">{text}</a>'
                f'</span>'
            )
        else:
            parts.append(f'<span class="cv-contact-item">{text}</span>')
    return "".join(parts)


def _render_contact_vertical(items: list) -> str:
    """Render contact items vertically (for sidebar)."""
    parts = []
    for item in items:
        text = _esc(item["text"])
        if item.get("href"):
            href = _esc(item["href"])
            short = _esc(item["text"])
            parts.append(
                f'<div class="cv-contact-item">'
                f'<a href="{href}" data-short-url="{short}">{text}</a>'
                f'</div>'
            )
        else:
            parts.append(f'<div class="cv-contact-item">{text}</div>')
    return "".join(parts)


def _render_contact_with_icons(items: list) -> str:
    """Render contact items with icon circles (for creative header)."""
    parts = []
    for item in items:
        text = _esc(item["text"])
        icon = _esc(item.get("icon", ""))
        icon_html = f'<span class="cv-contact-icon">{icon}</span>'
        if item.get("href"):
            href = _esc(item["href"])
            short = _esc(item["text"])
            parts.append(
                f'<div class="cv-contact-item">'
                f'{icon_html}'
                f'<a href="{href}" data-short-url="{short}">{text}</a>'
                f'</div>'
            )
        else:
            parts.append(
                f'<div class="cv-contact-item">'
                f'{icon_html}'
                f'<span>{text}</span>'
                f'</div>'
            )
    return "".join(parts)


# ---------------------------------------------------------------------------
# Shared section renderers
# ---------------------------------------------------------------------------


def _render_certifications_grid(certs: list) -> str:
    """Render certifications as a 2-column grid (classic)."""
    if not certs:
        return ""
    h = '<div class="cv-certifications-list">'
    for c in certs:
        name = _esc(c.get("name", ""))
        issuer = _esc(c.get("issuer", ""))
        h += '<div class="cv-certification-item">'
        h += f'<span class="cv-certification-name">{name}</span>'
        if issuer:
            h += f'<span class="cv-certification-issuer">{issuer}</span>'
        h += '</div>'
    h += '</div>'
    return h


def _render_certifications_list(certs: list) -> str:
    """Render certifications as a vertical list (modern-sidebar, two-column)."""
    if not certs:
        return ""
    h = '<div class="cv-certifications-list">'
    for c in certs:
        name = _esc(c.get("name", ""))
        issuer = _esc(c.get("issuer", ""))
        h += '<div class="cv-certification-item">'
        h += f'<span class="cv-certification-name">{name}</span>'
        if issuer:
            h += f'<span class="cv-certification-issuer">{issuer}</span>'
        h += '</div>'
    h += '</div>'
    return h


def _render_certifications_creative(certs: list) -> str:
    """Render certifications with badge icon (creative)."""
    if not certs:
        return ""
    h = ""
    for c in certs:
        name = _esc(c.get("name", ""))
        issuer = _esc(c.get("issuer", ""))
        h += '<div class="cv-certification-item">'
        h += '<span class="cv-certification-badge">\u2713</span>'
        h += '<div class="cv-certification-info">'
        h += f'<div class="cv-certification-name">{name}</div>'
        if issuer:
            h += f'<div class="cv-certification-issuer">{issuer}</div>'
        h += '</div></div>'
    return h


def _render_languages_inline(languages: list) -> str:
    """Render languages inline (classic)."""
    if not languages:
        return ""
    h = '<div class="cv-languages-list">'
    for lang_item in languages:
        name = _esc(lang_item.get("name", ""))
        level = _esc(lang_item.get("level", ""))
        h += '<span class="cv-language-item">'
        h += f'<span class="cv-language-name">{name}</span>'
        if level:
            h += f' <span class="cv-language-level">({level})</span>'
        h += '</span>'
    h += '</div>'
    return h


def _render_languages_vertical(languages: list) -> str:
    """Render languages as vertical list with level on right."""
    if not languages:
        return ""
    h = '<div class="cv-languages-list">'
    for lang_item in languages:
        name = _esc(lang_item.get("name", ""))
        level = _esc(lang_item.get("level", ""))
        h += '<div class="cv-language-item">'
        h += f'<span class="cv-language-name">{name}</span>'
        if level:
            h += f'<span class="cv-language-level">{level}</span>'
        h += '</div>'
    h += '</div>'
    return h


def _language_level_to_dots(level: str) -> int:
    """Convert a language level string to a number of filled dots (out of 5)."""
    level_lower = level.lower().strip() if level else ""
    mapping = {
        "natif": 5, "native": 5, "maternelle": 5, "langue maternelle": 5,
        "courant": 4, "fluent": 4, "bilingue": 5, "bilingual": 5,
        "avance": 4, "advanced": 4, "c2": 5, "c1": 4,
        "intermediaire": 3, "intermediate": 3, "b2": 3, "b1": 3,
        "elementaire": 2, "elementary": 2, "a2": 2,
        "debutant": 1, "beginner": 1, "a1": 1,
        "professionnel": 4, "professional": 4,
    }
    return mapping.get(level_lower, 3)


def _render_languages_dots(languages: list) -> str:
    """Render languages with dot indicators (creative)."""
    if not languages:
        return ""
    h = '<div class="cv-languages-list">'
    for lang_item in languages:
        name = _esc(lang_item.get("name", ""))
        level = lang_item.get("level", "")
        filled = _language_level_to_dots(level)
        h += '<div class="cv-language-item">'
        h += f'<span class="cv-language-name">{name}</span>'
        h += '<div class="cv-language-dots">'
        for i in range(5):
            cls = "cv-language-dot filled" if i < filled else "cv-language-dot"
            h += f'<span class="{cls}"></span>'
        h += '</div>'
        h += '</div>'
    h += '</div>'
    return h


def _render_soft_skills(soft_skills: list) -> str:
    """Render soft skills as a list."""
    if not soft_skills:
        return ""
    h = '<div class="cv-soft-skills-list">'
    for s in soft_skills:
        name = _esc(s) if isinstance(s, str) else _esc(s.get("name", ""))
        h += f'<span class="cv-soft-skill">{name}</span>'
    h += '</div>'
    return h


def _render_projects(projects: list, lang: str) -> str:
    """Render project items."""
    if not projects:
        return ""
    h = ""
    for proj in projects:
        name = _esc(proj.get("name", ""))
        desc = _esc(proj.get("description", ""))
        url = proj.get("url", "")
        h += '<div class="cv-project-item">'
        if url:
            short = _esc(_linkedin_short(url))
            h += (
                f'<div class="cv-project-name">'
                f'<a href="{_esc(url)}" data-short-url="{short}">{name}</a>'
                f'</div>'
            )
        else:
            h += f'<div class="cv-project-name">{name}</div>'
        if desc:
            h += f'<div class="cv-project-description">{desc}</div>'
        h += '</div>'
    return h


# ---------------------------------------------------------------------------
# Skill level helpers
# ---------------------------------------------------------------------------


def _skill_level_percent(skill: dict) -> int:
    """Get a skill level as a percentage (0-100)."""
    level = skill.get("level", 0)
    if isinstance(level, (int, float)):
        if level <= 5:
            return int(level * 20)
        return min(int(level), 100)
    return 60


def _render_skills_bars(skills: list) -> str:
    """Render skills with level bars (modern-sidebar)."""
    if not skills:
        return ""
    h = '<div class="cv-skills-list">'
    for s in skills:
        name = _esc(s.get("name", ""))
        pct = _skill_level_percent(s)
        h += '<div class="cv-skill-item">'
        h += f'<span class="cv-skill-name">{name}</span>'
        h += '<div class="cv-skill-bar">'
        h += f'<div class="cv-skill-level" style="width: {pct}%"></div>'
        h += '</div></div>'
    h += '</div>'
    return h


def _render_skills_progress(skills: list) -> str:
    """Render skills with progress bars and percentage (creative)."""
    if not skills:
        return ""
    h = ""
    for s in skills:
        name = _esc(s.get("name", ""))
        pct = _skill_level_percent(s)
        h += '<div class="cv-skill-item">'
        h += '<div class="cv-skill-header">'
        h += f'<span class="cv-skill-name">{name}</span>'
        h += f'<span class="cv-skill-percent">{pct}%</span>'
        h += '</div>'
        h += '<div class="cv-skill-bar">'
        h += f'<div class="cv-skill-level" style="width: {pct}%"></div>'
        h += '</div></div>'
    return h


def _render_skills_tags(skills: list, highlight_names: list = None) -> str:
    """Render skills as tags/pills (two-column)."""
    if not skills:
        return ""
    if highlight_names is None:
        highlight_names = []
    highlight_set = {n.lower() for n in highlight_names}

    h = '<div class="cv-skills-list">'
    for s in skills:
        name = _esc(s.get("name", ""))
        cls = "cv-skill-tag"
        if name.lower() in highlight_set or s.get("highlight"):
            cls += " highlight"
        h += f'<span class="{cls}">{name}</span>'
    h += '</div>'
    return h


# ---------------------------------------------------------------------------
# Template: Classic (ATS-Optimised)
# ---------------------------------------------------------------------------


def render_classic(p: dict, color: str, lang: str, sections: dict) -> str:
    """Generate the Classic CV inner HTML.

    Port of generateClassicCV() from print.html.
    """
    first_name = _esc(p.get("firstName", ""))
    last_name = _esc(p.get("lastName", ""))
    title = _esc(p.get("title", ""))
    summary_dict = p.get("summary") or {}
    summary = summary_dict if isinstance(summary_dict, str) else summary_dict.get("default", "")
    hard_skills = p.get("hard_skills") or []
    soft_skills = p.get("soft_skills") or []
    experiences = p.get("experiences") or []
    education = p.get("education") or []
    certifications = p.get("certifications") or []
    languages = p.get("languages") or []
    projects = p.get("projects") or []
    highlight_skills = p.get("highlight_skills") or []

    contact_items = _build_contact_items(p)

    h = ""

    # Header
    h += '<div class="cv-header">'
    h += f'<div class="cv-name">{first_name} {last_name}</div>'
    h += f'<div class="cv-title">{title}</div>'
    h += f'<div class="cv-contact">{_render_contact_inline(contact_items)}</div>'
    h += '</div>'

    # Summary
    h += f'<div class="cv-section{_hidden_cls(sections, "summary")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("profile", lang))}</h2>'
    h += f'<div class="cv-summary">{_esc(summary)}</div>'
    h += '</div>'

    # Skills
    h += f'<div class="cv-section cv-skills-section{_hidden_cls(sections, "skills")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("skills", lang))}</h2>'
    h += _render_skills_by_category(hard_skills, highlight_skills)
    h += '</div>'

    # Experience
    h += f'<div class="cv-section{_hidden_cls(sections, "experience")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("experience", lang))}</h2>'
    for exp in experiences:
        h += _render_experience(exp, lang)
    h += '</div>'

    # Education
    h += f'<div class="cv-section{_hidden_cls(sections, "education")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("education", lang))}</h2>'
    for edu in education:
        h += _render_education_classic(edu)
    h += '</div>'

    # Certifications
    h += f'<div class="cv-section{_hidden_cls(sections, "certifications")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("certifications", lang))}</h2>'
    h += _render_certifications_grid(certifications)
    h += '</div>'

    # Languages
    h += f'<div class="cv-section{_hidden_cls(sections, "languages")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("languages", lang))}</h2>'
    h += _render_languages_inline(languages)
    h += '</div>'

    # Projects (optional)
    h += f'<div class="cv-section{_hidden_cls(sections, "projects")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("projects", lang))}</h2>'
    h += _render_projects(projects, lang)
    h += '</div>'

    return h


# ---------------------------------------------------------------------------
# Template: Modern Sidebar
# ---------------------------------------------------------------------------


def render_modern_sidebar(p: dict, color: str, lang: str, sections: dict) -> str:
    """Generate the Modern Sidebar CV inner HTML.

    Port of generateModernSidebarCV().
    """
    first_name = _esc(p.get("firstName", ""))
    last_name = _esc(p.get("lastName", ""))
    title = _esc(p.get("title", ""))
    summary_dict = p.get("summary") or {}
    summary = summary_dict if isinstance(summary_dict, str) else summary_dict.get("default", "")
    hard_skills = p.get("hard_skills") or []
    soft_skills = p.get("soft_skills") or []
    experiences = p.get("experiences") or []
    education = p.get("education") or []
    certifications = p.get("certifications") or []
    languages = p.get("languages") or []
    projects = p.get("projects") or []

    contact_items = _build_contact_items(p)

    h = ""

    # ---- Sidebar ----
    h += '<aside class="cv-sidebar">'

    # Sidebar header
    h += '<div class="cv-header">'
    h += f'<div class="cv-name">{first_name} {last_name}</div>'
    h += f'<div class="cv-title">{title}</div>'
    h += '</div>'

    # Sidebar contact
    h += '<div class="cv-section">'
    h += f'<h2 class="cv-section-title">{_esc(_t("contact", lang))}</h2>'
    h += f'<div class="cv-contact">{_render_contact_vertical(contact_items)}</div>'
    h += '</div>'

    # Sidebar skills (with level bars)
    h += f'<div class="cv-section{_hidden_cls(sections, "skills")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("skills", lang))}</h2>'
    h += _render_skills_bars(hard_skills)
    h += '</div>'

    # Sidebar languages
    h += f'<div class="cv-section{_hidden_cls(sections, "languages")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("languages", lang))}</h2>'
    h += _render_languages_vertical(languages)
    h += '</div>'

    # Sidebar soft skills
    h += '<div class="cv-section">'
    h += f'<h2 class="cv-section-title">{_esc(_t("qualities", lang))}</h2>'
    h += _render_soft_skills(soft_skills)
    h += '</div>'

    h += '</aside>'

    # ---- Main ----
    h += '<main class="cv-main">'

    # Summary
    h += f'<div class="cv-section{_hidden_cls(sections, "summary")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("profile", lang))}</h2>'
    h += f'<div class="cv-summary">{_esc(summary)}</div>'
    h += '</div>'

    # Experience
    h += f'<div class="cv-section{_hidden_cls(sections, "experience")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("experience", lang))}</h2>'
    for exp in experiences:
        h += _render_experience(exp, lang)
    h += '</div>'

    # Education
    h += f'<div class="cv-section{_hidden_cls(sections, "education")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("education", lang))}</h2>'
    for edu in education:
        h += _render_education_classic(edu)
    h += '</div>'

    # Certifications
    h += f'<div class="cv-section{_hidden_cls(sections, "certifications")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("certifications", lang))}</h2>'
    h += _render_certifications_list(certifications)
    h += '</div>'

    h += '</main>'

    return h


# ---------------------------------------------------------------------------
# Template: Two-Column
# ---------------------------------------------------------------------------


def render_two_column(p: dict, color: str, lang: str, sections: dict) -> str:
    """Generate the Two-Column CV inner HTML.

    Port of generateTwoColumnCV().
    """
    first_name = _esc(p.get("firstName", ""))
    last_name = _esc(p.get("lastName", ""))
    title = _esc(p.get("title", ""))
    summary_dict = p.get("summary") or {}
    summary = summary_dict if isinstance(summary_dict, str) else summary_dict.get("default", "")
    hard_skills = p.get("hard_skills") or []
    soft_skills = p.get("soft_skills") or []
    experiences = p.get("experiences") or []
    education = p.get("education") or []
    certifications = p.get("certifications") or []
    languages = p.get("languages") or []
    projects = p.get("projects") or []
    highlight_skills = p.get("highlight_skills") or []

    contact_items = _build_contact_items(p)

    h = ""

    # Header (full width)
    h += '<div class="cv-header">'
    h += '<div class="cv-header-left">'
    h += f'<div class="cv-name">{first_name} {last_name}</div>'
    h += f'<div class="cv-title">{title}</div>'
    h += '</div>'
    h += '<div class="cv-header-right">'
    h += f'<div class="cv-contact">{_render_contact_vertical(contact_items)}</div>'
    h += '</div>'
    h += '</div>'

    # ---- Left column ----
    h += '<aside class="cv-column-left">'

    # Skills (tags)
    h += f'<div class="cv-section{_hidden_cls(sections, "skills")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("skills", lang))}</h2>'
    h += _render_skills_tags(hard_skills, highlight_skills)
    h += '</div>'

    # Languages
    h += f'<div class="cv-section{_hidden_cls(sections, "languages")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("languages", lang))}</h2>'
    h += _render_languages_vertical(languages)
    h += '</div>'

    # Soft skills
    h += '<div class="cv-section">'
    h += f'<h2 class="cv-section-title">{_esc(_t("qualities", lang))}</h2>'
    h += _render_soft_skills(soft_skills)
    h += '</div>'

    # Education
    h += f'<div class="cv-section{_hidden_cls(sections, "education")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("education", lang))}</h2>'
    for edu in education:
        h += _render_education_classic(edu)
    h += '</div>'

    # Certifications
    h += f'<div class="cv-section{_hidden_cls(sections, "certifications")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("certifications", lang))}</h2>'
    h += _render_certifications_list(certifications)
    h += '</div>'

    h += '</aside>'

    # ---- Right column ----
    h += '<main class="cv-column-right">'

    # Summary
    h += f'<div class="cv-section{_hidden_cls(sections, "summary")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("profile", lang))}</h2>'
    h += f'<div class="cv-summary">{_esc(summary)}</div>'
    h += '</div>'

    # Experience
    h += f'<div class="cv-section{_hidden_cls(sections, "experience")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("experience", lang))}</h2>'
    for exp in experiences:
        h += _render_experience(exp, lang)
    h += '</div>'

    # Projects (optional)
    h += f'<div class="cv-section{_hidden_cls(sections, "projects")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("projects", lang))}</h2>'
    h += _render_projects(projects, lang)
    h += '</div>'

    h += '</main>'

    return h


# ---------------------------------------------------------------------------
# Template: Creative (Timeline)
# ---------------------------------------------------------------------------


def render_creative(p: dict, color: str, lang: str, sections: dict) -> str:
    """Generate the Creative CV inner HTML.

    Port of generateCreativeCV().
    """
    first_name = _esc(p.get("firstName", ""))
    last_name = _esc(p.get("lastName", ""))
    title = _esc(p.get("title", ""))
    summary_dict = p.get("summary") or {}
    summary = summary_dict if isinstance(summary_dict, str) else summary_dict.get("default", "")
    hard_skills = p.get("hard_skills") or []
    soft_skills = p.get("soft_skills") or []
    experiences = p.get("experiences") or []
    education = p.get("education") or []
    certifications = p.get("certifications") or []
    languages = p.get("languages") or []
    projects = p.get("projects") or []

    contact_items = _build_contact_items(p)

    h = ""

    # Header (hero / gradient style with icons)
    h += '<div class="cv-header">'
    h += '<div class="cv-header-content">'
    h += f'<div class="cv-name">{first_name} {last_name}</div>'
    h += f'<div class="cv-title">{title}</div>'
    h += f'<div class="cv-contact">{_render_contact_with_icons(contact_items)}</div>'
    h += '</div>'
    h += '</div>'

    # Body (table layout: main + aside)
    h += '<div class="cv-body">'

    # ---- Main ----
    h += '<main class="cv-main">'

    # Summary (quote style)
    h += f'<div class="cv-section{_hidden_cls(sections, "summary")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("profile", lang))}</h2>'
    h += f'<div class="cv-summary">{_esc(summary)}</div>'
    h += '</div>'

    # Experience (timeline with cv-experience-list)
    h += f'<div class="cv-section{_hidden_cls(sections, "experience")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("experience", lang))}</h2>'
    h += '<div class="cv-experience-list">'
    for exp in experiences:
        h += _render_experience_creative(exp, lang)
    h += '</div>'
    h += '</div>'

    # Projects (optional)
    h += f'<div class="cv-section{_hidden_cls(sections, "projects")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("projects", lang))}</h2>'
    h += _render_projects(projects, lang)
    h += '</div>'

    h += '</main>'

    # ---- Aside ----
    h += '<aside class="cv-aside">'

    # Skills (with progress bars + percentage)
    h += f'<div class="cv-section{_hidden_cls(sections, "skills")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("skills", lang))}</h2>'
    h += _render_skills_progress(hard_skills)
    h += '</div>'

    # Languages (dots)
    h += f'<div class="cv-section{_hidden_cls(sections, "languages")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("languages", lang))}</h2>'
    h += _render_languages_dots(languages)
    h += '</div>'

    # Soft skills
    h += '<div class="cv-section">'
    h += f'<h2 class="cv-section-title">{_esc(_t("qualities", lang))}</h2>'
    h += _render_soft_skills(soft_skills)
    h += '</div>'

    # Education
    h += f'<div class="cv-section{_hidden_cls(sections, "education")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("education", lang))}</h2>'
    for edu in education:
        h += _render_education_classic(edu)
    h += '</div>'

    # Certifications (with badge)
    h += f'<div class="cv-section{_hidden_cls(sections, "certifications")}">'
    h += f'<h2 class="cv-section-title">{_esc(_t("certifications", lang))}</h2>'
    h += _render_certifications_creative(certifications)
    h += '</div>'

    h += '</aside>'

    h += '</div>'  # .cv-body

    return h


# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

_RENDERERS = {
    "classic": render_classic,
    "modern-sidebar": render_modern_sidebar,
    "two-column": render_two_column,
    "creative": render_creative,
}

# ---------------------------------------------------------------------------
# Main public functions
# ---------------------------------------------------------------------------


def render_cv(
    profile: dict,
    template: str = "classic",
    color: str = "#2563eb",
    sections: dict = None,
) -> str:
    """Return a complete standalone HTML document for the CV.

    Parameters
    ----------
    profile:
        The profile dictionary (master or adapted).
    template:
        One of ``"classic"``, ``"modern-sidebar"``, ``"two-column"``,
        ``"creative"``.
    color:
        CSS accent colour (e.g. ``"#2563eb"``).
    sections:
        Which sections to show. Merged with DEFAULT_SECTIONS.

    Returns
    -------
    str
        A complete ``<!DOCTYPE html>`` document with embedded CSS.
    """
    lang = profile.get("lang", "fr")

    # Merge sections with defaults
    merged_sections = dict(DEFAULT_SECTIONS)
    if sections:
        merged_sections.update(sections)

    # Get the renderer
    renderer = _RENDERERS.get(template)
    if renderer is None:
        raise ValueError(
            f"Unknown template {template!r}. "
            f"Choose from: {', '.join(sorted(_RENDERERS))}"
        )

    # Generate inner HTML
    inner_html = renderer(profile, color, lang, merged_sections)

    # Generate full CSS
    full_css = get_full_css(template, color)

    # Build document title
    last_name = profile.get("lastName", "CV")
    first_name = profile.get("firstName", "")
    target_company = profile.get("target_company", "")
    now = date.today()
    date_suffix = now.strftime("%Y%m")
    title_parts = [f"CV_{_esc(last_name)}-{_esc(first_name)}"]
    if target_company:
        title_parts.append(f"_{_esc(target_company)}")
    title_parts.append(f"_{date_suffix}")
    doc_title = "".join(title_parts)

    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="{_esc(lang)}">\n'
        f'<head>\n'
        f'  <meta charset="UTF-8">\n'
        f'  <title>{doc_title}</title>\n'
        f'  <style>\n'
        f'    @page {{ size: A4; margin: 0; }}\n'
        f'    * {{ margin: 0; padding: 0; box-sizing: border-box;'
        f' -webkit-print-color-adjust: exact !important;'
        f' print-color-adjust: exact !important; }}\n'
        f'    html, body {{ width: 210mm; margin: 0; padding: 0; }}\n'
        f'    {full_css}\n'
        f'    .cv-page {{ --cv-accent: {_esc(color)};'
        f' --accent-color: {_esc(color)}; }}\n'
        f'  </style>\n'
        f'</head>\n'
        f'<body>\n'
        f'  <div class="cv-page">\n'
        f'    {inner_html}\n'
        f'  </div>\n'
        f'</body>\n'
        f'</html>\n'
    )


def render_cover_letter(profile: dict) -> str:
    """Return the cover letter text from the profile, if any."""
    return profile.get("cover_letter", "")
