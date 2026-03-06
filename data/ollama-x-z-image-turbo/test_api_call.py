import requests

# Définir l'URL d'Ollama
url = 'http://127.0.0.1:11434/api/generate'  # ou l'endpoint approprié

# Exemple de requête pour le modèle
payload = {"model": "x/z-image-turbo", "prompt": "a cartoon cat astronaut on the moon, with big eyes and colorful fur"}

# Appel de l'API
response = requests.post(url, json=payload)

# Affichage du résultat
if response.status_code == 200:
    print("Image générée avec succès:", response.json())
else:
    print("Erreur lors de la génération d'image:", response.text)