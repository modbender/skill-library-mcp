#!/usr/bin/env python3


"""
Script d’envoi de SMS via l’API Free Mobile
Usage: ./FreeMobile_sms.py -m "votre message"

Authentification via variables d’environnement :
  FREEMOBILE_SMS_USER : identifiant Free Mobile
  FREEMOBILE_SMS_API_KEY  : clé API
"""

import argparse
import os
import sys
import requests


def send_sms(user, api_key, message, timeout=10):
    """
    Envoie un SMS via l’API Free Mobile

    Returns:
        tuple: (success: bool, status_code: int, message: str)
    """
    url = "https://smsapi.free-mobile.fr/sendmsg"

    # Limite de longueur SMS
    if len(message) > 160:
        print(f"Avertissement: message tronqué à 160 caractères", file=sys.stderr)
        message = message[:160]

    params = {
        'user': user,
        'pass': api_key,
        'msg': message
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)

        # Analyse du code de retour
        if response.status_code == 200:
            return True, 200, "200 : SMS envoyé avec succès"
        elif response.status_code == 400:
            return False, 400, "400 : Paramètre manquant ou invalide"
        elif response.status_code == 402:
            return False, 402, "402 : Quota SMS dépassé ou option désactivée"
        elif response.status_code == 403:
            return False, 403, "403 : Clé API incorrecte"
        elif response.status_code == 500:
            return False, 500, "500 : Erreur serveur Free Mobile"
        else:
            return False, response.status_code, f"Erreur HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return False, 0, f"Timeout après {timeout}s"
    except requests.exceptions.ConnectionError:
        return False, 0, "Erreur de connexion réseau"
    except Exception as e:
        return False, 0, f"Erreur: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Envoi de SMS via l’API Free Mobile',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s -m "Serveur démarré"
  %(prog)s --message "Alerte CPU haute" --timeout 15

Configuration requise:
  export FREEMOBILE_SMS_USER="12345678"
  export FREEMOBILE_SMS_API_KEY="VotreClé"

Limites API Free Mobile:
  - 200-250 SMS/jour maximum
  - 160 caractères max par SMS
  - Uniquement vers votre numéro Free Mobile
  - Espacer les envois d’au moins 10 secondes
        """
    )

    parser.add_argument('-m', '--message', required=True, help='Message à envoyer')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Timeout requête HTTP (défaut: 10s)')

    args = parser.parse_args()

    # Récupération des identifiants depuis variables d’environnement
    user = os.environ.get('FREEMOBILE_SMS_USER')
    api_key = os.environ.get('FREEMOBILE_SMS_API_KEY')

    if not user or not api_key:
        print("Erreur: Variables d’environnement manquantes", file=sys.stderr)
        print("", file=sys.stderr)
        print("Définissez les variables suivantes :", file=sys.stderr)
        print("  export FREEMOBILE_SMS_USER=\"votre_identifiant\"", file=sys.stderr)
        print("  export FREEMOBILE_SMS_API_KEY=\"votre_clé_api\"", file=sys.stderr)
        print("", file=sys.stderr)
        print("Ces identifiants sont disponibles sur :", file=sys.stderr)
        print("  mobile.free.fr > Mes options > Notifications par SMS", file=sys.stderr)
        sys.exit(1)

    # Envoi du SMS
    success, code, msg = send_sms(user, api_key, args.message, args.timeout)

    if success:
        print(msg)
        sys.exit(0)
    else:
        print(f"Échec: {msg} (code {code})", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
