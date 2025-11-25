# 🌐 Guide ngrok - Exposer Card Connector

## Installation de ngrok

### Sur macOS (avec Homebrew)
```bash
brew install ngrok/ngrok/ngrok
```

### Sur Linux
```bash
# Télécharger depuis https://ngrok.com/download
# Ou avec snap:
snap install ngrok
```

### Sur Windows
Télécharge depuis : https://ngrok.com/download

---

## Configuration de ngrok

### 1. Créer un compte (gratuit)
1. Va sur https://dashboard.ngrok.com/signup
2. Crée un compte gratuit
3. Récupère ton **authtoken** depuis le dashboard

### 2. Configurer l'authtoken
```bash
ngrok config add-authtoken TON_AUTHTOKEN_ICI
```

---

## Créer un tunnel vers Card Connector

### Méthode 1 : Interface web (recommandée)

```bash
# Lancer ngrok
ngrok http 8000
```

Cela va :
- Créer un tunnel vers `http://localhost:8000`
- Afficher l'URL publique (ex: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`)
- Ouvrir une interface web sur http://localhost:4040

### Méthode 2 : En arrière-plan

```bash
# Lancer en arrière-plan
ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &

# Voir l'URL
sleep 3
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool | grep -A 2 "public_url"
```

---

## Récupérer l'URL du tunnel

### Via l'interface web
Ouvre dans ton navigateur : http://localhost:4040

Tu verras :
- L'URL publique (ex: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`)
- Les requêtes en temps réel
- Les réponses HTTP

### Via l'API ngrok
```bash
curl http://localhost:4040/api/tunnels | python3 -m json.tool
```

### Via la ligne de commande
```bash
# Script simple pour récupérer l'URL
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
tunnels = data.get('tunnels', [])
if tunnels:
    print('🌐 URL publique:', tunnels[0]['public_url'])
    print('📡 Webhook endpoint:', tunnels[0]['public_url'] + '/api/v1/webhooks/skaleet/card')
else:
    print('❌ Aucun tunnel actif')
"
```

---

## URL du webhook pour Skaleet

Une fois ngrok lancé, l'URL du webhook sera :

```
https://xxxx-xx-xx-xx-xx.ngrok-free.app/api/v1/webhooks/skaleet/card
```

Remplace `xxxx-xx-xx-xx-xx` par ton URL ngrok.

---

## Tester le tunnel

### 1. Vérifier que le service répond
```bash
# Via l'URL ngrok
curl https://TON-URL-NGROK.ngrok-free.app/api/v1/health
```

### 2. Tester un webhook
```bash
curl -X POST https://TON-URL-NGROK.ngrok-free.app/api/v1/webhooks/skaleet/card \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2401597",
    "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
    "type": "card",
    "event": "card.status.activation_requested",
    "data": {
      "cardId": 12345,
      "panAlias": "CMSPARTNER-12345"
    }
  }'
```

---

## Scripts utiles

### Script pour lancer ngrok et afficher l'URL
Crée un fichier `start-ngrok.sh` :

```bash
#!/bin/bash
echo "🚀 Lancement de ngrok..."
ngrok http 8000 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

sleep 3

echo ""
echo "✅ ngrok lancé (PID: $NGROK_PID)"
echo ""
echo "🌐 Récupération de l'URL..."

URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
tunnels = data.get('tunnels', [])
if tunnels:
    print(tunnels[0]['public_url'])
else:
    print('EN_ATTENTE')
" 2>/dev/null)

if [ "$URL" != "EN_ATTENTE" ] && [ ! -z "$URL" ]; then
    echo "✅ URL publique: $URL"
    echo ""
    echo "📡 Webhook endpoint pour Skaleet:"
    echo "   $URL/api/v1/webhooks/skaleet/card"
    echo ""
    echo "💡 Interface web ngrok: http://localhost:4040"
    echo ""
    echo "Pour arrêter: kill $NGROK_PID"
else
    echo "⏳ En attente de l'URL..."
    echo "💡 Ouvre http://localhost:4040 pour voir l'URL"
fi
```

Rendre exécutable :
```bash
chmod +x start-ngrok.sh
./start-ngrok.sh
```

---

## Dépannage

### Erreur : "authtoken required"
```bash
ngrok config add-authtoken TON_AUTHTOKEN
```

### Erreur : "port already in use"
```bash
# Trouver le processus
lsof -ti:4040

# Arrêter
kill $(lsof -ti:4040)
```

### Erreur : "authentication failed"
- Vérifie que ton authtoken est correct
- Va sur https://dashboard.ngrok.com/get-started/your-authtoken
- Réinstalle l'authtoken

### Le tunnel ne fonctionne pas
1. Vérifie que le service tourne : `curl http://localhost:8000/api/v1/health`
2. Vérifie les logs ngrok : `cat /tmp/ngrok.log`
3. Vérifie l'interface web : http://localhost:4040

---

## Alternatives à ngrok

Si ngrok ne fonctionne pas, tu peux utiliser :

### localtunnel
```bash
npx --yes localtunnel --port 8000
```

### cloudflared (Cloudflare Tunnel)
```bash
brew install cloudflare/cloudflare/cloudflared
cloudflared tunnel --url http://localhost:8000
```

---

## Notes importantes

⚠️ **Sécurité** :
- Les URLs ngrok gratuites sont publiques
- N'utilise que pour le développement/test
- Ne partage pas l'URL publiquement

⚠️ **Limitations gratuites** :
- URL change à chaque redémarrage
- Limite de connexions simultanées
- Limite de bande passante

✅ **Pour la production** :
- Utilise un domaine fixe avec ngrok (plan payant)
- Ou configure un reverse proxy avec un domaine réel

---

## Commandes rapides

```bash
# Lancer ngrok
ngrok http 8000

# Voir l'URL
curl http://localhost:4040/api/tunnels | python3 -m json.tool

# Arrêter ngrok
pkill ngrok

# Voir les logs
tail -f /tmp/ngrok.log
```

