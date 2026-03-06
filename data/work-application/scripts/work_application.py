#!/usr/bin/env python3
"""
work_application.py - Main CLI entry point for the openclaw-skill-work-application skill.

Usage:
    python work_application.py profile show
    python work_application.py profile validate
    python work_application.py render [--template TEMPLATE] [--color COLOR] [--lang LANG] [--output FILE]
    python work_application.py scrape [--platforms PLATFORMS]
    python work_application.py analyze
    python work_application.py deep-analyze [--max N]
    python work_application.py report <url>
    python work_application.py track list [--status STATUS]
    python work_application.py track add COMPANY POSITION [options]
    python work_application.py track update COMPANY STATUS
    python work_application.py config
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow importing sibling modules from the same scripts/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _profile
import _validators
import _cv_renderer
import _pdf_exporter
import _scraper
import _analyzer
import _tracker
import _report
from _profile import ProfileError


# ---------------------------------------------------------------------------
# Jobs directory
# ---------------------------------------------------------------------------

_JOBS_DIR = Path.home() / ".openclaw" / "data" / "work-application" / "jobs"


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_profile_show(args):
    """Load and display the master profile."""
    try:
        profile = _profile.load_master_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
    title = profile.get("title", "-")
    email = profile.get("email", "-")
    phone = profile.get("phone", "-")
    location = profile.get("location", "-")

    hard_skills = profile.get("hard_skills") or []
    soft_skills = profile.get("soft_skills") or []
    experiences = profile.get("experiences") or []
    education = profile.get("education") or []

    print("=== Profil Master ===")
    print(f"  Nom:               {name}")
    print(f"  Titre:             {title}")
    print(f"  Email:             {email}")
    print(f"  Telephone:         {phone}")
    print(f"  Localisation:      {location}")
    print(f"  Competences tech.: {len(hard_skills)}")
    print(f"  Soft skills:       {len(soft_skills)}")
    print(f"  Experiences:       {len(experiences)}")
    print(f"  Formations:        {len(education)}")


def cmd_profile_validate(args):
    """Load adapted profile and run validation."""
    try:
        profile = _profile.load_adapted_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    report = _validators.validate_profile(profile)

    if report["errors"]:
        print("Erreurs:")
        for err in report["errors"]:
            print(f"  [ERREUR] {err}")

    if report["warnings"]:
        print("Avertissements:")
        for warn in report["warnings"]:
            print(f"  [WARN]   {warn}")

    if report["valid"]:
        print("\nStatut: VALIDE")
    else:
        print("\nStatut: INVALIDE")
        sys.exit(1)


def cmd_render(args):
    """Render CV to HTML."""
    try:
        cfg = _profile.load_config()
        _profile._check_permission(cfg, "allow_export")
        profile = _profile.load_adapted_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    template = args.template or cfg.get("default_template", "classic")
    color = args.color or cfg.get("default_color", "#2563eb")
    lang = args.lang or cfg.get("default_lang", "fr")

    # Set lang on the profile so the renderer picks it up
    profile["lang"] = lang

    try:
        html_output = _cv_renderer.render_cv(profile, template=template, color=color)
    except ValueError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_output, encoding="utf-8")
        print(f"CV genere: {output_path}")
    else:
        print(html_output)

    # PDF export if requested
    if args.pdf:
        # We need an HTML file on disk for Playwright to render
        if args.output:
            html_file = Path(args.output)
        else:
            # Write to a temp file if no --output was given
            import tempfile
            tmp = tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8"
            )
            tmp.write(html_output)
            tmp.close()
            html_file = Path(tmp.name)

        pdf_path = Path(args.pdf)
        try:
            result = asyncio.run(
                _pdf_exporter.export_pdf(str(html_file), str(pdf_path))
            )
            print(f"PDF exporte: {result}")
        except ImportError as e:
            print(f"Erreur: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            # Clean up temp file if we created one
            if not args.output:
                html_file.unlink(missing_ok=True)


def cmd_scrape(args):
    """Run the job scraper."""
    try:
        cfg = _profile.load_config()
        _profile._check_permission(cfg, "allow_scrape")
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    scraper_cfg = cfg.get("scraper", {})

    # Filter searches by platform if requested
    if args.platforms:
        requested = {p.strip().lower() for p in args.platforms.split(",")}
        searches = scraper_cfg.get("searches", [])
        scraper_cfg["searches"] = [
            s for s in searches if s.get("platform", "").lower() in requested
        ]

    # Build a config dict the scraper expects (searches at top level + scraper settings)
    scraper_run_cfg = dict(cfg)
    scraper_run_cfg["searches"] = scraper_cfg.get("searches", [])
    scraper_run_cfg["scraper"] = scraper_cfg

    print("Lancement du scraping...")
    scraper = _scraper.JobScraper(scraper_run_cfg)
    jobs = asyncio.run(scraper.scrape_all())
    print(f"  {len(jobs)} offres brutes trouvees.")

    # Filter
    filters = scraper_cfg.get("filters", {})
    already_applied = _tracker.get_already_applied()
    jobs = _scraper.filter_jobs(jobs, filters, already_applied)
    print(f"  {len(jobs)} offres apres filtrage.")

    # Deduplicate
    jobs = _scraper.deduplicate(jobs, already_applied)
    print(f"  {len(jobs)} offres apres deduplication.")

    # Save to jobs-found.md
    _JOBS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = _JOBS_DIR / "jobs-found.md"

    md = _analyzer.format_markdown(jobs, title="Offres trouvees")
    output_path.write_text(md, encoding="utf-8")
    print(f"  Resultats sauvegardes: {output_path}")


def cmd_analyze(args):
    """Analyze scraped jobs."""
    jobs_found_path = _JOBS_DIR / "jobs-found.md"

    if not jobs_found_path.exists():
        print(
            f"Erreur: Fichier introuvable: {jobs_found_path}\n"
            "  Lancez d'abord: python work_application.py scrape",
            file=sys.stderr,
        )
        sys.exit(1)

    content = jobs_found_path.read_text(encoding="utf-8")
    jobs = _analyzer.parse_jobs_markdown(content)

    if not jobs:
        print("Aucune offre a analyser.")
        return

    try:
        master = _profile.load_master_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyse de {len(jobs)} offres...")

    # Rank
    ranked = _analyzer.rank_jobs(jobs, master)

    # Save ranked
    _JOBS_DIR.mkdir(parents=True, exist_ok=True)
    ranked_path = _JOBS_DIR / "jobs-ranked.md"
    ranked_md = _analyzer.format_markdown(ranked, title="Offres classees par pertinence")
    ranked_path.write_text(ranked_md, encoding="utf-8")
    print(f"  Classement sauvegarde: {ranked_path}")

    # Select top
    selected = _analyzer.select_top(ranked)
    selected_path = _JOBS_DIR / "jobs-selected.md"
    selected_md = _analyzer.format_selected_markdown(selected)
    selected_path.write_text(selected_md, encoding="utf-8")
    print(
        f"  Selection sauvegardee: {selected_path} "
        f"({len(selected.get('cdi', []))} CDI, {len(selected.get('freelance', []))} Freelance)"
    )


def cmd_deep_analyze(args):
    """Deep analyze jobs by scraping their actual pages."""
    jobs_found_path = _JOBS_DIR / "jobs-found.md"

    if not jobs_found_path.exists():
        print(
            f"Erreur: Fichier introuvable: {jobs_found_path}\n"
            "  Lancez d'abord: python work_application.py scrape",
            file=sys.stderr,
        )
        sys.exit(1)

    content = jobs_found_path.read_text(encoding="utf-8")
    jobs = _analyzer.parse_jobs_markdown(content)

    if not jobs:
        print("Aucune offre a analyser.")
        return

    try:
        master = _profile.load_master_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    max_jobs = args.max or 30

    def on_progress(idx, total, job, msg):
        platform = job.get("platform", job.get("_raw", {}).get("platform", ""))
        location = job.get("location", "")
        print(f"  [{idx}/{total}] {msg}")
        if platform or location:
            print(f"           {platform} - {location}")

    print(f"Analyse approfondie de {len(jobs)} offres (top {max_jobs})...")
    print("Lancement du navigateur...\n")

    try:
        results = asyncio.run(
            _analyzer.deep_analyze(
                jobs, master, max_jobs=max_jobs, on_progress=on_progress,
            )
        )
    except ImportError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n  {len(results)} offres analysees avec succes.")

    # Select top CDI + Freelance
    selected = _analyzer.select_top(results)
    cdi_count = len(selected.get("cdi", []))
    freelance_count = len(selected.get("freelance", []))

    # Save results
    _JOBS_DIR.mkdir(parents=True, exist_ok=True)
    selected_path = _JOBS_DIR / "jobs-selected.md"
    selected_md = _analyzer.format_selected_markdown(selected)
    selected_path.write_text(selected_md, encoding="utf-8")

    print(f"  Selection sauvegardee: {selected_path} ({cdi_count} CDI, {freelance_count} Freelance)")

    # Print summary
    for label, key in [("CDI", "cdi"), ("Freelance", "freelance")]:
        group = selected.get(key, [])
        if group:
            print(f"\n  TOP {label}:")
            for i, job in enumerate(group, 1):
                analysis = job.get("analysis", {})
                pct = analysis.get("match_percentage", 0)
                title = job.get("title", "-")[:40]
                company = job.get("company", "-")[:20]
                remote = analysis.get("remote", "-")
                salary = analysis.get("salary") or job.get("salary", "-")
                matched = analysis.get("matched_skills", [])
                skills_str = ", ".join(s["name"] for s in matched[:6])

                print(f"    {i}. [{pct}%] {title}")
                print(f"       {company} | {remote} | {salary}")
                if skills_str:
                    print(f"       Skills: {skills_str}")

                gaps = analysis.get("missing_skills", [])
                if gaps:
                    gap_str = ", ".join(g["name"] for g in gaps)
                    print(f"       Gaps: {gap_str}")


def cmd_report(args):
    """Generate a full analysis report for a single job offer URL."""
    try:
        cfg = _profile.load_config()
        master = _profile.load_master_profile()
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    url = args.url

    def on_progress(step, msg):
        print(f"  [{step}/10] {msg}")

    print(f"Generation du rapport pour : {url}\n")

    try:
        report = asyncio.run(
            _report.generate_report(url, master, cfg, on_progress=on_progress)
        )
    except ImportError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    if not report.get("success"):
        print(f"\nErreur: {report.get('error', 'Erreur inconnue')}", file=sys.stderr)
        sys.exit(1)

    # Format and display
    markdown = _report.format_report_markdown(report)
    print(f"\n{'=' * 60}")
    print(markdown)

    # Save
    try:
        paths = _report.save_report(report, markdown)
        print(f"Rapport sauvegarde :")
        print(f"  MD   : {paths['md']}")
        print(f"  JSON : {paths['json']}")
    except Exception as e:
        print(f"Erreur sauvegarde : {e}", file=sys.stderr)

    # If report_mode == "cv+analysis", generate adapted CV
    report_mode = cfg.get("report_mode", "analysis")
    if report_mode == "cv+analysis" and report.get("success"):
        try:
            _profile._check_permission(cfg, "allow_write")
            # Build adapted profile from matched skills
            adapted = dict(master)
            matched_names = [
                s["name"] for s in report["skills"].get("matched_skills", [])
            ]
            if matched_names:
                adapted["_matched_skills"] = matched_names
                adapted["_job_title"] = report.get("job_title", "")
                adapted["_job_company"] = report.get("company_name", "")
            _profile.save_adapted_profile(adapted, cfg)
            print(f"\n  CV adapte sauvegarde (mode: cv+analysis)")
        except ProfileError as e:
            print(f"  Note: CV adapte non genere ({e})")


def cmd_track_list(args):
    """List candidatures as a formatted table."""
    rows = _tracker.list_applications(status=args.status)

    if not rows:
        print("Aucune candidature trouvee.")
        return

    # Table header
    header = f"{'Date':<10} {'Entreprise':<20} {'Poste':<25} {'Lieu':<18} {'Statut':<12} {'Action':<10}"
    separator = "-" * len(header)

    print(header)
    print(separator)

    for row in rows:
        date = row.get("date", "-")
        company = row.get("company", "-")[:20]
        position = row.get("position", "-")[:25]
        location = row.get("location", "-")[:18]
        status_icon = row.get("status", "-")
        action = row.get("action", "-")[:10]

        print(f"{date:<10} {company:<20} {position:<25} {location:<18} {status_icon:<12} {action:<10}")

    print(separator)
    print(f"{len(rows)} candidature(s)")


def cmd_track_add(args):
    """Add a new candidature."""
    try:
        cfg = _profile.load_config()
        _profile._check_permission(cfg, "allow_tracking")
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    _tracker.log_application(
        company=args.company,
        position=args.position,
        location=args.location or "",
        type_=args.type or "CDI",
        salary=args.salary or "",
        source=args.source or "",
        url=args.url or "",
        contact=args.contact or "",
        email=args.email or "",
        phone=args.phone or "",
        notes=args.notes or "",
    )

    print(f"Candidature ajoutee: {args.company} - {args.position}")


def cmd_track_update(args):
    """Update candidature status."""
    try:
        cfg = _profile.load_config()
        _profile._check_permission(cfg, "allow_tracking")
    except ProfileError as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

    valid_statuses = ["en_attente", "entretien", "negociation", "offre", "refus", "desistement"]
    if args.status not in valid_statuses:
        print(
            f"Erreur: Statut invalide '{args.status}'.\n"
            f"  Valeurs possibles: {', '.join(valid_statuses)}",
            file=sys.stderr,
        )
        sys.exit(1)

    found = _tracker.update_status(args.company, args.status)

    if found:
        print(f"Statut mis a jour: {args.company} -> {args.status}")
    else:
        print(f"Erreur: Candidature introuvable pour '{args.company}'.", file=sys.stderr)
        sys.exit(1)


def cmd_config(args):
    """Display current configuration."""
    cfg = _profile.load_config()
    print(json.dumps(cfg, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="work_application",
        description="CLI pour le skill openclaw-skill-work-application.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commande principale")

    # --- profile ---
    profile_parser = subparsers.add_parser("profile", help="Gestion du profil")
    profile_sub = profile_parser.add_subparsers(dest="profile_action", help="Action")

    profile_sub.add_parser("show", help="Afficher le profil master")
    profile_sub.add_parser("validate", help="Valider le profil adapte")

    # --- render ---
    render_parser = subparsers.add_parser("render", help="Generer le CV en HTML")
    render_parser.add_argument(
        "--template",
        choices=["classic", "modern-sidebar", "two-column", "creative"],
        default=None,
        help="Template de CV (defaut: depuis config)",
    )
    render_parser.add_argument(
        "--color",
        default=None,
        help="Couleur d'accent en hexadecimal (ex: #2563eb)",
    )
    render_parser.add_argument(
        "--lang",
        choices=["fr", "en"],
        default=None,
        help="Langue du CV (defaut: depuis config)",
    )
    render_parser.add_argument(
        "--output",
        default=None,
        help="Fichier HTML de sortie (defaut: stdout)",
    )
    render_parser.add_argument(
        "--pdf",
        default=None,
        help="Exporter en PDF (necessite Playwright). Ex: --pdf cv.pdf",
    )

    # --- scrape ---
    scrape_parser = subparsers.add_parser("scrape", help="Lancer le scraping d'offres")
    scrape_parser.add_argument(
        "--platforms",
        default=None,
        help="Plateformes a scraper (separe par des virgules, ex: free-work,wttj)",
    )

    # --- analyze ---
    subparsers.add_parser("analyze", help="Analyser les offres scrapees (rapide, titre/URL)")

    # --- deep-analyze ---
    deep_parser = subparsers.add_parser(
        "deep-analyze",
        help="Analyse approfondie (scrape le contenu des offres, necessite Playwright)",
    )
    deep_parser.add_argument(
        "--max",
        type=int,
        default=30,
        help="Nombre max d'offres a analyser en profondeur (defaut: 30)",
    )

    # --- report ---
    report_parser = subparsers.add_parser(
        "report",
        help="Rapport d'analyse complet pour une offre (scrape + analyse multi-dimensions)",
    )
    report_parser.add_argument("url", help="URL de l'offre d'emploi a analyser")

    # --- track ---
    track_parser = subparsers.add_parser("track", help="Suivi des candidatures")
    track_sub = track_parser.add_subparsers(dest="track_action", help="Action")

    # track list
    track_list_parser = track_sub.add_parser("list", help="Lister les candidatures")
    track_list_parser.add_argument(
        "--status",
        choices=["en_attente", "entretien", "negociation", "offre", "refus", "desistement"],
        default=None,
        help="Filtrer par statut",
    )

    # track add
    track_add_parser = track_sub.add_parser("add", help="Ajouter une candidature")
    track_add_parser.add_argument("company", help="Nom de l'entreprise")
    track_add_parser.add_argument("position", help="Poste vise")
    track_add_parser.add_argument("--location", default=None, help="Lieu")
    track_add_parser.add_argument("--type", default="CDI", help="Type de contrat (defaut: CDI)")
    track_add_parser.add_argument("--salary", default=None, help="Salaire / TJM")
    track_add_parser.add_argument("--source", default=None, help="Source de l'offre")
    track_add_parser.add_argument("--url", default=None, help="URL de l'offre")
    track_add_parser.add_argument("--contact", default=None, help="Nom du contact")
    track_add_parser.add_argument("--email", default=None, help="Email du contact")
    track_add_parser.add_argument("--phone", default=None, help="Telephone du contact")
    track_add_parser.add_argument("--notes", default=None, help="Notes")

    # track update
    track_update_parser = track_sub.add_parser("update", help="Mettre a jour le statut")
    track_update_parser.add_argument("company", help="Nom de l'entreprise")
    track_update_parser.add_argument(
        "status",
        choices=["en_attente", "entretien", "negociation", "offre", "refus", "desistement"],
        help="Nouveau statut",
    )

    # --- config ---
    subparsers.add_parser("config", help="Afficher la configuration actuelle")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "profile":
        if args.profile_action == "show":
            cmd_profile_show(args)
        elif args.profile_action == "validate":
            cmd_profile_validate(args)
        else:
            parser.parse_args(["profile", "--help"])

    elif args.command == "render":
        cmd_render(args)

    elif args.command == "scrape":
        cmd_scrape(args)

    elif args.command == "analyze":
        cmd_analyze(args)

    elif args.command == "deep-analyze":
        cmd_deep_analyze(args)

    elif args.command == "report":
        cmd_report(args)

    elif args.command == "track":
        if args.track_action == "list":
            cmd_track_list(args)
        elif args.track_action == "add":
            cmd_track_add(args)
        elif args.track_action == "update":
            cmd_track_update(args)
        else:
            parser.parse_args(["track", "--help"])

    elif args.command == "config":
        cmd_config(args)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
