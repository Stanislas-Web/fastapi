#!/bin/bash

# Script pour lancer cloudflared (alternative à ngrok et localtunnel)

echo "🚀 Lancement de cloudflared pour Card Connector..."
echo ""

# Vérifier que cloudflared est installé
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared n'est pas installé"
    echo ""
    echo "Pour installer sur macOS:"
    echo "  brew install cloudflare/cloudflare/cloudflared"
    echo ""
    echo "Ou télécharge depuis:"
    echo "  https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
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

echo "✅ Service accessible sur port 8000"
echo ""
echo "🌐 Lancement de cloudflared..."
echo ""
echo "⏳ cloudflared va créer un tunnel public..."
echo "   (Cela peut prendre quelques secondes)"
echo ""

# Lancer cloudflared
cloudflared tunnel --url http://localhost:8000

