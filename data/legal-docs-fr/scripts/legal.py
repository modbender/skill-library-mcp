#!/usr/bin/env python3
"""Générateur de documents juridiques français pour freelances/micro-entrepreneurs."""

import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path.home() / ".freelance"
LEGAL_DIR = DATA_DIR / "legal"
CONFIG_FILE = DATA_DIR / "config.json"


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def format_euro(amount):
    s = f"{abs(amount):,.2f}".replace(",", "\u00a0").replace(".", ",")
    sign = "-" if amount < 0 else ""
    return f"{sign}{s}\u00a0€"


def get_initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][0].upper() if parts else "F"


def get_next_devis_number():
    year = datetime.now().strftime("%Y")
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    existing = []
    for f in LEGAL_DIR.glob(f"DEV-{year}-*.json"):
        try:
            num = int(f.stem.split("-")[2])
            existing.append(num)
        except (IndexError, ValueError):
            pass
    next_num = max(existing, default=0) + 1
    return f"DEV-{year}-{next_num:03d}"


def parse_item(item_str):
    parts = item_str.rsplit(":", 2)
    if len(parts) != 3:
        print(f"Erreur : format d'item invalide « {item_str} ». Attendu: 'description:quantité:prix'", file=sys.stderr)
        sys.exit(1)
    desc = parts[0]
    try:
        qty = float(parts[1])
        price = float(parts[2])
    except ValueError:
        print(f"Erreur : quantité ou prix non numérique dans « {item_str} »", file=sys.stderr)
        sys.exit(1)
    return {"description": desc, "quantity": qty, "unit_price": price, "total": round(qty * price, 2)}


# ─── HTML Base Template ───────────────────────────────────────────────

def html_wrap(title, body_content, accent="#2563eb"):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @media print {{
    body {{ margin: 0; padding: 20px; }}
    .container {{ box-shadow: none !important; max-width: 100% !important; }}
    .no-print {{ display: none; }}
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: #f5f5f5;
    margin: 0;
    padding: 40px 20px;
    color: #333;
    line-height: 1.6;
  }}
  .container {{
    max-width: 800px;
    margin: 0 auto;
    background: #fff;
    padding: 50px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.08);
    border-radius: 4px;
  }}
  h1 {{ color: {accent}; margin-top: 0; }}
  h2 {{ color: #1a1a1a; border-bottom: 2px solid {accent}; padding-bottom: 6px; margin-top: 30px; }}
  h3 {{ color: #374151; margin-top: 24px; }}
  p, li {{ font-size: 14px; color: #444; }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 30px; border-bottom: 3px solid {accent}; padding-bottom: 20px; }}
  .legal-section {{ margin-bottom: 20px; }}
  .signature-box {{ border: 1px dashed #ccc; border-radius: 6px; padding: 30px; margin-top: 30px; text-align: center; color: #999; }}
</style>
</head>
<body>
<div class="container">
{body_content}
</div>
<div class="no-print" style="text-align: center; margin-top: 20px; color: #94a3b8; font-size: 13px;">
  <p>Pour exporter en PDF : Fichier → Imprimer → Enregistrer au format PDF</p>
</div>
</body>
</html>"""


def provider_header_html(provider, doc_type, doc_date=None):
    name = provider.get("name", "Prestataire")
    initials = get_initials(name)
    date_str = doc_date or datetime.now().strftime("%d/%m/%Y")
    return f"""<div class="header">
    <div>
      <div style="width: 60px; height: 60px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; margin-bottom: 12px;">{initials}</div>
      <h2 style="margin: 0 0 4px 0; border: none; padding: 0; color: #1a1a1a;">{name}</h2>
      <p style="margin: 2px 0; color: #666; font-size: 13px;">{provider.get('address', '')}</p>
      <p style="margin: 2px 0; color: #666; font-size: 13px;">SIRET : {provider.get('siret', 'Non renseigné')}</p>
      {"<p style='margin: 2px 0; color: #666; font-size: 13px;'>" + provider.get('email') + "</p>" if provider.get('email') else ""}
      {"<p style='margin: 2px 0; color: #666; font-size: 13px;'>" + provider.get('phone') + "</p>" if provider.get('phone') else ""}
    </div>
    <div style="text-align: right;">
      <h1 style="margin: 0; font-size: 28px;">{doc_type}</h1>
      <p style="margin: 8px 0; color: #666;">Date : {date_str}</p>
    </div>
  </div>"""


# ─── CGV ──────────────────────────────────────────────────────────────

def generate_cgv(args):
    config = load_config()
    provider = config.get("provider", {})
    name = provider.get("name", args.nom or "Le Prestataire")
    siret = provider.get("siret", args.siret or "Non renseigné")
    address = provider.get("address", args.adresse or "Non renseignée")
    email = provider.get("email", args.email or "")
    micro = config.get("micro_entreprise", True)

    mediateur = args.mediateur or "Médiateur de la consommation — consulter la liste officielle sur economie.gouv.fr"
    tribunal = args.tribunal or address.split(",")[-1].strip() if address != "Non renseignée" else "du siège du prestataire"

    tva_mention = "TVA non applicable, article 293 B du Code général des impôts." if micro else ""

    body = provider_header_html(provider, "CONDITIONS GÉNÉRALES DE VENTE") + f"""
  <p style="text-align: center; font-style: italic; color: #666; margin-bottom: 30px;">Applicables à compter du {datetime.now().strftime("%d/%m/%Y")}</p>

  <h2>Article 1 — Objet et champ d'application</h2>
  <p>Les présentes Conditions Générales de Vente (CGV) s'appliquent à l'ensemble des prestations de services réalisées par <strong>{name}</strong>, SIRET {siret}, ci-après « le Prestataire », pour le compte de ses clients professionnels, ci-après « le Client ».</p>
  <p>Toute commande de prestation implique l'acceptation sans réserve des présentes CGV.</p>

  <h2>Article 2 — Conditions de passation des commandes</h2>
  <p>Toute prestation fait l'objet d'un devis préalable, établi gratuitement par le Prestataire. La commande est considérée comme ferme et définitive à réception du devis signé portant la mention « Bon pour accord », accompagné le cas échéant de l'acompte prévu.</p>

  <h2>Article 3 — Tarifs et modalités de paiement</h2>
  <p>Les prix sont indiqués en euros hors taxes. {tva_mention}</p>
  <p>Les factures sont payables à <strong>30 jours</strong> à compter de la date d'émission, par virement bancaire, sauf conditions particulières mentionnées sur le devis.</p>
  <p><strong>Pénalités de retard :</strong> En cas de retard de paiement, des pénalités seront exigibles au taux de <strong>3 fois le taux d'intérêt légal</strong> en vigueur, calculées sur le montant TTC de la somme restant due, sans qu'un rappel soit nécessaire (articles L441-10 et D441-5 du Code de commerce).</p>
  <p>Une <strong>indemnité forfaitaire de 40 €</strong> pour frais de recouvrement sera également due de plein droit (article D441-5 du Code de commerce).</p>

  <h2>Article 4 — Délais d'exécution</h2>
  <p>Les délais d'exécution sont donnés à titre indicatif et sont convenus d'un commun accord entre les parties. Le Prestataire s'engage à mettre en œuvre tous les moyens nécessaires pour respecter les délais convenus. Tout retard ne peut donner lieu à des dommages et intérêts ni à l'annulation de la commande.</p>

  <h2>Article 5 — Propriété intellectuelle</h2>
  <p>La cession des droits de propriété intellectuelle sur les livrables est subordonnée au <strong>paiement intégral</strong> du prix convenu. Jusqu'au paiement complet, le Prestataire reste titulaire de l'ensemble des droits de propriété intellectuelle sur les travaux réalisés.</p>
  <p>La cession couvre le droit de reproduction et de représentation, pour une durée illimitée, dans le monde entier, sur tout support, sauf accord contraire écrit.</p>

  <h2>Article 6 — Responsabilité et garanties</h2>
  <p>Le Prestataire est tenu à une obligation de moyens. Il ne saurait être tenu responsable des dommages indirects (perte de chiffre d'affaires, perte de données, atteinte à l'image, etc.) résultant de l'exécution de la prestation.</p>
  <p>En tout état de cause, la responsabilité du Prestataire est limitée au montant total de la prestation commandée.</p>

  <h2>Article 7 — Résiliation</h2>
  <p>En cas de manquement grave de l'une des parties à ses obligations contractuelles, le contrat pourra être résilié de plein droit <strong>15 jours</strong> après l'envoi d'une mise en demeure par lettre recommandée avec accusé de réception restée sans effet.</p>
  <p>En cas de résiliation anticipée par le Client, les prestations réalisées restent dues au prorata du travail effectué, et tout acompte versé reste acquis au Prestataire.</p>

  <h2>Article 8 — Force majeure</h2>
  <p>Aucune des parties ne pourra être tenue responsable de l'inexécution de ses obligations en cas de force majeure telle que définie par l'article 1218 du Code civil. La partie invoquant la force majeure en informera l'autre dans les meilleurs délais.</p>

  <h2>Article 9 — Droit applicable et juridiction compétente</h2>
  <p>Les présentes CGV sont soumises au droit français. En cas de litige, les parties rechercheront une solution amiable. À défaut, les <strong>tribunaux compétents de {tribunal}</strong> seront seuls compétents.</p>

  <h2>Article 10 — Médiation</h2>
  <p>Conformément aux articles L611-1 et suivants du Code de la consommation, le Client peut recourir gratuitement à un médiateur de la consommation en vue de la résolution amiable de tout litige :</p>
  <p style="background: #f8fafc; padding: 12px; border-radius: 4px; border-left: 3px solid #2563eb;">{mediateur}</p>

  <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 40px; font-size: 11px; color: #94a3b8;">
    <p>{name} — SIRET {siret} — {address}</p>
    {f"<p>{email}</p>" if email else ""}
  </div>"""

    return html_wrap(f"CGV — {name}", body), "cgv"


# ─── MENTIONS LÉGALES ─────────────────────────────────────────────────

def generate_mentions(args):
    config = load_config()
    provider = config.get("provider", {})
    name = provider.get("name", args.nom or "Non renseigné")
    siret = provider.get("siret", args.siret or "Non renseigné")
    address = provider.get("address", args.adresse or "Non renseignée")
    email = provider.get("email", args.email or "Non renseigné")
    phone = provider.get("phone", args.phone or "")
    hebergeur = args.hebergeur or "Non renseigné"
    site = args.site or "ce site"
    dpo = args.dpo or email

    body = f"""
  <h1>Mentions légales</h1>
  <p style="color: #666; font-style: italic;">En vigueur au {datetime.now().strftime("%d/%m/%Y")}</p>

  <h2>1. Identité de l'éditeur</h2>
  <p><strong>{name}</strong></p>
  <p>Adresse : {address}</p>
  <p>SIRET : {siret}</p>
  <p>Email : {email}</p>
  {f"<p>Téléphone : {phone}</p>" if phone else ""}

  <h2>2. Directeur de la publication</h2>
  <p>{name}</p>

  <h2>3. Hébergeur</h2>
  <p>{hebergeur}</p>

  <h2>4. Propriété intellectuelle</h2>
  <p>L'ensemble du contenu de {site} (textes, images, vidéos, logos, icônes, etc.) est protégé par le droit d'auteur et le droit de la propriété intellectuelle. Toute reproduction, représentation, modification ou adaptation, totale ou partielle, est interdite sans autorisation écrite préalable de l'éditeur.</p>

  <h2>5. Protection des données personnelles (RGPD)</h2>
  <h3>Responsable de traitement</h3>
  <p>{name} — {email}</p>

  <h3>Finalités du traitement</h3>
  <ul>
    <li>Gestion de la relation client et des demandes de contact</li>
    <li>Envoi de communications commerciales (avec consentement)</li>
    <li>Mesure d'audience et amélioration du site</li>
  </ul>

  <h3>Droits des personnes</h3>
  <p>Conformément au Règlement Général sur la Protection des Données (UE 2016/679) et à la loi Informatique et Libertés, vous disposez des droits suivants :</p>
  <ul>
    <li>Droit d'accès, de rectification et d'effacement de vos données</li>
    <li>Droit à la limitation du traitement</li>
    <li>Droit à la portabilité de vos données</li>
    <li>Droit d'opposition au traitement</li>
    <li>Droit d'introduire une réclamation auprès de la CNIL</li>
  </ul>
  <p>Pour exercer ces droits, contactez : <strong>{dpo}</strong></p>

  <h3>Durée de conservation</h3>
  <p>Les données sont conservées pour la durée nécessaire aux finalités pour lesquelles elles sont collectées, et conformément à la législation en vigueur.</p>

  <h2>6. Cookies</h2>
  <p>{site} peut utiliser des cookies pour assurer son bon fonctionnement et mesurer l'audience. Vous pouvez à tout moment modifier vos préférences en matière de cookies dans les paramètres de votre navigateur.</p>
  <p>Cookies essentiels : nécessaires au fonctionnement du site (pas de consentement requis).<br>
  Cookies analytiques : soumis à votre consentement préalable conformément à la directive ePrivacy et aux recommandations de la CNIL.</p>

  <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 40px; font-size: 11px; color: #94a3b8;">
    <p>Dernière mise à jour : {datetime.now().strftime("%d/%m/%Y")}</p>
  </div>"""

    return html_wrap(f"Mentions légales — {name}", body), "mentions"


# ─── CONTRAT DE PRESTATION ────────────────────────────────────────────

def generate_contrat(args):
    config = load_config()
    provider = config.get("provider", {})
    pname = provider.get("name", args.nom or "Le Prestataire")
    paddress = provider.get("address", "")
    psiret = provider.get("siret", "Non renseigné")
    pemail = provider.get("email", "")
    micro = config.get("micro_entreprise", True)

    client_name = args.client
    client_address = args.client_address or ""
    client_siret = args.client_siret or ""
    mission = args.mission
    montant = args.montant
    duree = args.duree
    date_debut = args.date_debut or datetime.now().strftime("%d/%m/%Y")
    non_sollicitation = args.non_sollicitation

    tva_mention = "TVA non applicable, article 293 B du CGI." if micro else ""
    montant_str = format_euro(montant)

    body = provider_header_html(provider, "CONTRAT DE PRESTATION DE SERVICES") + f"""
  <p style="text-align: center; font-weight: 600; color: #666; margin-bottom: 30px;">Établi le {datetime.now().strftime("%d/%m/%Y")}</p>

  <h2>Entre les soussignés</h2>
  <div style="display: flex; gap: 30px; margin-bottom: 20px;">
    <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px;">
      <p style="font-weight: 700; text-transform: uppercase; font-size: 11px; color: #94a3b8; letter-spacing: 1px; margin: 0 0 8px 0;">Le Prestataire</p>
      <p style="font-weight: 600; margin: 4px 0;">{pname}</p>
      <p style="margin: 2px 0; font-size: 13px; color: #666;">{paddress}</p>
      <p style="margin: 2px 0; font-size: 13px; color: #666;">SIRET : {psiret}</p>
    </div>
    <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px;">
      <p style="font-weight: 700; text-transform: uppercase; font-size: 11px; color: #94a3b8; letter-spacing: 1px; margin: 0 0 8px 0;">Le Client</p>
      <p style="font-weight: 600; margin: 4px 0;">{client_name}</p>
      {f'<p style="margin: 2px 0; font-size: 13px; color: #666;">{client_address}</p>' if client_address else ""}
      {f'<p style="margin: 2px 0; font-size: 13px; color: #666;">SIRET : {client_siret}</p>' if client_siret else ""}
    </div>
  </div>

  <h2>Article 1 — Objet de la mission</h2>
  <p>Le Prestataire s'engage à réaliser pour le Client la mission suivante :</p>
  <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 16px; border-radius: 0 6px 6px 0; margin: 12px 0;">
    <p style="margin: 0; font-weight: 600;">{mission}</p>
  </div>

  <h2>Article 2 — Durée et calendrier</h2>
  <p>La mission débute le <strong>{date_debut}</strong> pour une durée de <strong>{duree}</strong>.</p>
  <p>Les délais sont convenus d'un commun accord. Tout retard significatif sera communiqué par le Prestataire dès qu'il en aura connaissance.</p>

  <h2>Article 3 — Prix et modalités de paiement</h2>
  <p>Le prix total de la prestation est fixé à <strong>{montant_str} HT</strong>. {tva_mention}</p>
  <p>Le règlement s'effectue selon l'échéancier suivant :</p>
  <ul>
    <li><strong>30%</strong> à la signature du présent contrat, soit {format_euro(round(montant * 0.3, 2))}</li>
    <li><strong>70%</strong> à la livraison des livrables, soit {format_euro(round(montant * 0.7, 2))}</li>
  </ul>
  <p>Les factures sont payables à 30 jours. En cas de retard, les pénalités prévues par la loi s'appliquent (3× taux légal + indemnité forfaitaire de 40 €).</p>

  <h2>Article 4 — Obligations du Prestataire</h2>
  <ul>
    <li>Réaliser la mission conformément aux règles de l'art et aux spécifications convenues</li>
    <li>Informer le Client de tout événement susceptible d'affecter la bonne exécution de la mission</li>
    <li>Respecter les délais convenus</li>
    <li>Remettre les livrables dans les formats et selon les modalités convenues</li>
  </ul>

  <h2>Article 5 — Obligations du Client</h2>
  <ul>
    <li>Fournir au Prestataire les informations et éléments nécessaires à la réalisation de la mission</li>
    <li>Respecter les délais de validation convenus</li>
    <li>Régler les factures dans les délais prévus</li>
    <li>Désigner un interlocuteur unique pour le suivi de la mission</li>
  </ul>

  <h2>Article 6 — Confidentialité</h2>
  <p>Chaque partie s'engage à ne pas divulguer les informations confidentielles de l'autre partie, obtenues dans le cadre de l'exécution du présent contrat. Cette obligation de confidentialité perdure pendant <strong>2 ans</strong> après la fin du contrat.</p>

  <h2>Article 7 — Propriété intellectuelle</h2>
  <p>La cession de l'ensemble des droits de propriété intellectuelle sur les livrables est subordonnée au <strong>paiement intégral</strong> du prix. Jusqu'au complet paiement, le Prestataire reste titulaire de l'ensemble des droits.</p>
  <p>Le Prestataire se réserve le droit de mentionner la réalisation de la mission à titre de référence, sauf opposition écrite du Client.</p>

  <h2>Article 8 — Résiliation</h2>
  <p>Chaque partie peut résilier le contrat en cas de manquement grave de l'autre partie, après mise en demeure par LRAR restée sans effet pendant <strong>15 jours</strong>.</p>
  <p>En cas de résiliation, les prestations réalisées et les frais engagés restent dus au prorata.</p>

  {"<h2>Article 9 — Clause de non-sollicitation</h2><p>Les parties s'interdisent mutuellement, pendant la durée du contrat et les <strong>12 mois</strong> suivant son terme, de solliciter ou embaucher tout collaborateur de l'autre partie ayant participé à la réalisation de la mission.</p>" if non_sollicitation else ""}

  <h2>Article {"10" if non_sollicitation else "9"} — Loi applicable</h2>
  <p>Le présent contrat est soumis au droit français. En cas de litige, les parties s'engagent à rechercher une solution amiable avant toute action judiciaire. À défaut, les tribunaux compétents seront saisis.</p>

  <div style="display: flex; gap: 30px; margin-top: 40px;">
    <div class="signature-box" style="flex: 1;">
      <p style="font-weight: 600; margin: 0 0 40px 0;">Le Prestataire</p>
      <p style="margin: 0;">Fait à _______________</p>
      <p>Le _______________</p>
      <p style="margin-top: 30px;">Signature :</p>
    </div>
    <div class="signature-box" style="flex: 1;">
      <p style="font-weight: 600; margin: 0 0 40px 0;">Le Client</p>
      <p style="margin: 0;">Fait à _______________</p>
      <p>Le _______________</p>
      <p style="margin-top: 30px;">Signature précédée de<br>« Bon pour accord » :</p>
    </div>
  </div>"""

    return html_wrap(f"Contrat — {pname} / {client_name}", body), client_name.lower().replace(' ', '-')


# ─── DEVIS ────────────────────────────────────────────────────────────

def generate_devis(args):
    config = load_config()
    provider = config.get("provider", {})
    micro = config.get("micro_entreprise", True)
    tva_rate = 0 if micro else config.get("tva_rate", 0.20)

    client_name = args.client
    items = [parse_item(i) for i in args.items]
    subtotal = round(sum(i["total"] for i in items), 2)
    tva_amount = round(subtotal * tva_rate, 2)
    total_ttc = round(subtotal + tva_amount, 2)

    number = args.number or get_next_devis_number()
    devis_date = args.date or datetime.now().strftime("%Y-%m-%d")
    validite = (datetime.strptime(devis_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%d/%m/%Y")
    devis_date_display = datetime.strptime(devis_date, "%Y-%m-%d").strftime("%d/%m/%Y")

    tva_mention = "TVA non applicable, article 293 B du Code général des impôts." if micro else ""

    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #eee;">{item['description']}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']:g}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: right;">{format_euro(item['unit_price'])}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #eee; text-align: right; font-weight: 600;">{format_euro(item['total'])}</td>
        </tr>"""

    tva_line = ""
    if not micro and tva_rate > 0:
        tva_line = f"""
        <tr>
            <td colspan="3" style="padding: 8px 12px; text-align: right; color: #666;">TVA ({tva_rate*100:.0f}%)</td>
            <td style="padding: 8px 12px; text-align: right;">{format_euro(tva_amount)}</td>
        </tr>"""

    body = provider_header_html(provider, "DEVIS", devis_date_display) + f"""
  <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; flex: 0 0 45%;">
      <p style="font-weight: 700; text-transform: uppercase; font-size: 11px; color: #94a3b8; letter-spacing: 1px; margin: 0 0 8px 0;">Client</p>
      <p style="font-weight: 600; margin: 4px 0;">{client_name}</p>
    </div>
    <div style="text-align: right;">
      <p style="margin: 4px 0; font-size: 16px; font-weight: 600;">Devis n° {number}</p>
      <p style="margin: 4px 0; color: #666;">Valable jusqu'au : <strong>{validite}</strong></p>
    </div>
  </div>

  <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
    <thead>
      <tr style="background: #f8fafc;">
        <th style="padding: 12px; text-align: left; font-weight: 600; font-size: 13px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0;">Description</th>
        <th style="padding: 12px; text-align: center; font-weight: 600; font-size: 13px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0;">Qté</th>
        <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0;">Prix unit. HT</th>
        <th style="padding: 12px; text-align: right; font-weight: 600; font-size: 13px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0;">Total HT</th>
      </tr>
    </thead>
    <tbody>
      {items_html}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="3" style="padding: 12px 12px 6px; text-align: right; font-weight: 600;">Sous-total HT</td>
        <td style="padding: 12px 12px 6px; text-align: right; font-weight: 600;">{format_euro(subtotal)}</td>
      </tr>
      {tva_line}
      <tr style="background: #2563eb; color: white;">
        <td colspan="3" style="padding: 14px 12px; text-align: right; font-weight: 700; font-size: 16px; border-radius: 0 0 0 6px;">Total {'TTC' if not micro else ''}</td>
        <td style="padding: 14px 12px; text-align: right; font-weight: 700; font-size: 18px; border-radius: 0 0 6px 0;">{format_euro(total_ttc)}</td>
      </tr>
    </tfoot>
  </table>

  <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 16px; margin-bottom: 30px;">
    <p style="margin: 0 0 8px 0; font-weight: 700; color: #166534;">💳 Conditions de paiement</p>
    <p style="margin: 4px 0;">Paiement par virement bancaire, à 30 jours après acceptation du devis.</p>
    <p style="margin: 4px 0;">Un acompte de 30% sera demandé à la commande.</p>
    {f"<p style='margin: 4px 0; font-style: italic; color: #666;'>{tva_mention}</p>" if tva_mention else ""}
  </div>

  <div class="signature-box">
    <p style="font-weight: 600; margin: 0 0 8px 0;">Bon pour accord</p>
    <p style="margin: 0 0 30px 0; color: #666; font-size: 13px;">Date et signature du client, précédées de la mention « Bon pour accord »</p>
    <div style="height: 80px;"></div>
    <p style="margin: 0; font-size: 12px;">Ce devis est valable 30 jours à compter de sa date d'émission.</p>
  </div>"""

    # Save metadata
    devis_data = {
        "type": "devis",
        "number": number,
        "date": devis_date,
        "validite": validite,
        "client": client_name,
        "items": items,
        "subtotal": subtotal,
        "tva_rate": tva_rate,
        "tva_amount": tva_amount,
        "total_ttc": total_ttc,
    }

    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    json_path = LEGAL_DIR / f"{number}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(devis_data, f, ensure_ascii=False, indent=2)

    return html_wrap(f"Devis {number} — {client_name}", body), number


# ─── COMMANDS ─────────────────────────────────────────────────────────

def save_and_report(html, filename, doc_type, no_open=False):
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = filename.replace("/", "-").replace(" ", "-")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    html_path = LEGAL_DIR / f"{safe_name}.html"

    # For cgv and mentions, use fixed names (overwrite). For contrat/devis use unique names.
    if doc_type in ("cgv", "mentions"):
        html_path = LEGAL_DIR / f"{doc_type}.html"
    elif doc_type == "contrat":
        html_path = LEGAL_DIR / f"contrat-{safe_name}-{ts}.html"
    # devis already has unique number as filename

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Save metadata for listing
    meta_path = html_path.with_suffix(".json")
    if not meta_path.exists():
        meta = {
            "type": doc_type,
            "filename": html_path.name,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✓ {doc_type.upper()} généré(e)")
    print(f"  Fichier : {html_path}")

    if not no_open:
        webbrowser.open(f"file://{html_path}")

    return html_path


def cmd_generate(args):
    doc_type = args.doc_type

    if doc_type == "cgv":
        html, fname = generate_cgv(args)
        save_and_report(html, fname, "cgv", args.no_open)

    elif doc_type == "mentions":
        html, fname = generate_mentions(args)
        save_and_report(html, fname, "mentions", args.no_open)

    elif doc_type == "contrat":
        if not args.client or not args.mission or args.montant is None or not args.duree:
            print("Erreur : --client, --mission, --montant et --duree sont requis pour un contrat.", file=sys.stderr)
            sys.exit(1)
        html, fname = generate_contrat(args)
        save_and_report(html, fname, "contrat", args.no_open)

    elif doc_type == "devis":
        if not args.client or not args.items:
            print("Erreur : --client et --items sont requis pour un devis.", file=sys.stderr)
            sys.exit(1)
        html, fname = generate_devis(args)
        save_and_report(html, fname, "devis", args.no_open)

    else:
        print(f"Erreur : type de document inconnu « {doc_type} ». Types disponibles : cgv, mentions, contrat, devis", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    docs = []

    for json_file in sorted(LEGAL_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        doc_type = data.get("type", "inconnu")
        html_file = json_file.with_suffix(".html")
        docs.append({
            "type": doc_type,
            "date": data.get("date", ""),
            "filename": html_file.name if html_file.exists() else "—",
            "client": data.get("client", ""),
            "number": data.get("number", ""),
        })

    if args.json:
        print(json.dumps(docs, ensure_ascii=False, indent=2))
        return

    if not docs:
        print("Aucun document juridique généré.")
        return

    print(f"{'Type':<12} {'Date':<12} {'Client/N°':<25} {'Fichier'}")
    print("─" * 75)
    for d in docs:
        label = d.get("number") or d.get("client") or ""
        print(f"{d['type']:<12} {d['date']:<12} {label:<25} {d['filename']}")


def cmd_config(args):
    config = load_config()
    if not config:
        print("Aucune configuration trouvée.")
        print("Créez ~/.freelance/config.json ou utilisez le freelance-toolkit : python3 config.py set ...")
        return

    if args.json:
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return

    p = config.get("provider", {})
    print("Configuration prestataire (depuis ~/.freelance/config.json) :")
    print(f"  Nom       : {p.get('name', '—')}")
    print(f"  Adresse   : {p.get('address', '—')}")
    print(f"  SIRET     : {p.get('siret', '—')}")
    print(f"  Email     : {p.get('email', '—')}")
    print(f"  Téléphone : {p.get('phone', '—')}")
    print(f"  Micro-ent.: {'Oui' if config.get('micro_entreprise') else 'Non'}")


def main():
    parser = argparse.ArgumentParser(description="Générateur de documents juridiques pour freelances")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    sub = parser.add_subparsers(dest="command")

    # generate
    p_gen = sub.add_parser("generate", help="Générer un document juridique")
    p_gen.add_argument("doc_type", choices=["cgv", "mentions", "contrat", "devis"],
                       help="Type de document : cgv, mentions, contrat, devis")
    p_gen.add_argument("--no-open", action="store_true", help="Ne pas ouvrir dans le navigateur")
    # Common provider overrides
    p_gen.add_argument("--nom", default=None, help="Nom du prestataire (override config)")
    p_gen.add_argument("--siret", default=None, help="SIRET (override config)")
    p_gen.add_argument("--adresse", default=None, help="Adresse (override config)")
    p_gen.add_argument("--email", default=None, help="Email (override config)")
    p_gen.add_argument("--phone", default=None, help="Téléphone (override config)")
    # Mentions
    p_gen.add_argument("--hebergeur", default=None, help="Hébergeur du site web")
    p_gen.add_argument("--site", default=None, help="Nom du site web")
    p_gen.add_argument("--dpo", default=None, help="Contact DPO")
    # CGV
    p_gen.add_argument("--mediateur", default=None, help="Coordonnées du médiateur")
    p_gen.add_argument("--tribunal", default=None, help="Tribunal compétent")
    # Contrat
    p_gen.add_argument("--client", default=None, help="Nom du client")
    p_gen.add_argument("--client-address", default=None, help="Adresse du client")
    p_gen.add_argument("--client-siret", default=None, help="SIRET du client")
    p_gen.add_argument("--mission", default=None, help="Description de la mission")
    p_gen.add_argument("--montant", type=float, default=None, help="Montant HT")
    p_gen.add_argument("--duree", default=None, help="Durée de la mission")
    p_gen.add_argument("--date-debut", default=None, help="Date de début (JJ/MM/AAAA)")
    p_gen.add_argument("--non-sollicitation", action="store_true", help="Inclure clause de non-sollicitation")
    # Devis
    p_gen.add_argument("--items", nargs="+", default=None, help="Items (desc:qté:prix)")
    p_gen.add_argument("--number", default=None, help="Numéro de devis (auto si omis)")
    p_gen.add_argument("--date", default=None, help="Date (YYYY-MM-DD)")

    # list
    p_list = sub.add_parser("list", help="Lister les documents générés")
    p_list.add_argument("--json", action="store_true", help="Sortie JSON")

    # config
    p_cfg = sub.add_parser("config", help="Afficher la configuration")
    p_cfg.add_argument("--json", action="store_true", help="Sortie JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "generate": cmd_generate,
        "list": cmd_list,
        "config": cmd_config,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
