#!/bin/bash

# Script pour lancer ngrok et afficher l'URL du webhook

echo "🚀 Lancement de ngrok pour Card Connector..."
echo ""

# Vérifier que ngrok est installé
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok n'est pas installé"
    echo ""
    echo "Pour installer sur macOS:"
    echo "  brew install ngrok/ngrok/ngrok"
    echo ""
    echo "Ou télécharge depuis: https://ngrok.com/download"
    exit 1
fi

# Vérifier que le service tourne
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "⚠️ Le service n'est pas accessible sur le port 8000"
    echo "Lance d'abord le service avec:"
    echo "  docker compose -f docker-compose.custom-port.yml up -d"
    echo "  ou"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

# Arrêter ngrok s'il tourne déjà
pkill -f "ngrok http" 2>/dev/null
sleep 1

echo "✅ Service accessible sur port 8000"
echo ""
echo "🌐 Lancement du tunnel ngrok..."
echo ""

# Lancer ngrok en arrière-plan
ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

echo "⏳ Attente de l'URL ngrok (5 secondes)..."
sleep 5

# Récupérer l'URL
URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)

if [ ! -z "$URL" ]; then
    echo ""
    echo "=" | head -c 60 && echo ""
    echo "✅ NGROK ACTIF!"
    echo "=" | head -c 60 && echo ""
    echo ""
    echo "🌐 URL publique:"
    echo "   $URL"
    echo ""
    echo "📡 Webhook endpoint pour Skaleet:"
    echo "   $URL/api/v1/webhooks/skaleet/card"
    echo ""
    echo "💡 Interface web ngrok:"
    echo "   http://localhost:4040"
    echo ""
    echo "📝 Pour arrêter ngrok:"
    echo "   kill $NGROK_PID"
    echo "   ou"
    echo "   pkill -f 'ngrok http'"
    echo ""
    echo "=" | head -c 60 && echo ""
else
    echo ""
    echo "⚠️ Impossible de récupérer l'URL automatiquement"
    echo ""
    echo "💡 Ouvre http://localhost:4040 dans ton navigateur"
    echo "   pour voir l'URL du tunnel"
    echo ""
    echo "📝 Logs ngrok: /tmp/ngrok.log"
    echo "   PID: $NGROK_PID"
fi

