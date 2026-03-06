import sys
import json
import requests

def main():
    # 1. Récupération de l'input (soit argument, soit stdin)
    raw_input = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    
    try:
        data = json.loads(raw_input)
        
        # 2. NETTOYAGE : On cherche la clé 'invoice' ou 'invoice_data' 
        # Si l'IA envoie tout, on ne garde que la partie facture
        if isinstance(data, dict):
            if "invoice" in data:
                payload = data["invoice"]
            elif "invoice_data" in data:
                payload = data["invoice_data"]
            else:
                # Si 'invoice' n'est pas une clé, on vérifie si l'objet 
                # lui-même contient les champs attendus (client, jours, etc.)
                payload = data
        else:
            payload = data

        # 3. Envoi à Make.com
        url = "https://hook.eu1.make.com/fto1pw8gfyk2kwqm8bab4ujykpfx1izi"
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("OK")
        else:
            print(f"Erreur Make: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    main()
