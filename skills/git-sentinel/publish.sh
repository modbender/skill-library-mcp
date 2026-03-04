# Publicar usando el token de entorno o argumento
CLAWHUB_TOKEN=$1
if [ -z "$CLAWHUB_TOKEN" ]; then
    echo "❌ Error: Necesito un token de ClawHub."
    echo "Uso: ./publish.sh <TOKEN>"
    exit 1
fi

npx clawhub publish . --token "$CLAWHUB_TOKEN"
