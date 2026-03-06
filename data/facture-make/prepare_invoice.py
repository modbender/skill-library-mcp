import sys
import json
from datetime import datetime

def main():
    data = json.load(sys.stdin)

    now = datetime.now()

    client = data.get("client") or "Air Training Academy"
    tjm = int(data.get("tjm") or 280)
    mois = data.get("mois") or now.strftime("%B").lower()
    annee = int(data.get("annee") or now.year)
    jours = data.get("jours")

    if not jours:
        print(json.dumps({
            "error": "Le nombre de jours doit être précisé."
        }, ensure_ascii=False))
        sys.exit(1)

    jours = int(jours)

    libelle = f"Consulting {mois} {annee}"

    invoice = {
        "client": client,
        "jours": jours,
        "tjm": tjm,
        "libelle": libelle
    }

    confirmation_text = (
        f"Je vais créer une facture de {jours} jours pour {client}, "
        f"au tarif de {tjm} euros par jour, libellé {libelle}. "
        f"Confirmez-vous ?"
    )

    print(json.dumps({
        "invoice": invoice,
        "confirmation": confirmation_text
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
