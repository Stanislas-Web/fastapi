#!/bin/bash

# Script pour lancer localtunnel (alternative à ngrok)

echo "🚀 Lancement de localtunnel pour Card Connector..."
echo ""

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
echo "🌐 Lancement de localtunnel..."
echo ""
echo "⏳ localtunnel va créer un tunnel public..."
echo "   (Cela peut prendre quelques secondes)"
echo ""

# Lancer localtunnel
npx --yes localtunnel --port 8000

