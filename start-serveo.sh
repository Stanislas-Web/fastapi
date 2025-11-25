#!/bin/bash

# Script pour lancer serveo (SSH tunnel) - Alternative fiable à cloudflared

echo "🚀 Lancement de serveo pour Card Connector..."
echo ""

# Vérifier que SSH est disponible
if ! command -v ssh &> /dev/null; then
    echo "❌ SSH n'est pas disponible"
    echo "SSH est généralement installé par défaut sur macOS/Linux"
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
echo "🌐 Lancement de serveo (SSH tunnel)..."
echo ""
echo "⏳ serveo va créer un tunnel public..."
echo "   (Cela peut prendre quelques secondes)"
echo ""
echo "💡 Tu obtiendras une URL comme: https://xxxx.serveo.net"
echo ""

# Lancer serveo
ssh -R 80:localhost:8000 serveo.net

