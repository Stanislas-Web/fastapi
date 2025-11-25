# 🌐 Tunnels pour Card Connector

Guide pour exposer le service local sur Internet.

---

## Solution 1 : cloudflared (Cloudflare Tunnel) ⭐ Recommandé

### Installation
```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Linux
# Télécharge depuis https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### Utilisation
```bash
# Lancer cloudflared
cloudflared tunnel --url http://localhost:8000
```

Cela affichera :
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://xxxx-xx-xx-xx-xx.trycloudflare.com                                                |
+--------------------------------------------------------------------------------------------+
```

### URL du webhook
```
https://xxxx-xx-xx-xx-xx.trycloudflare.com/api/v1/webhooks/skaleet/card
```

### Avantages
- ✅ Gratuit
- ✅ Pas besoin de compte
- ✅ Rapide (Cloudflare)
- ✅ Pas de restriction IP

### Inconvénients
- ⚠️ URL change à chaque lancement
- ⚠️ Nécessite l'installation

---

## Solution 2 : serveo (SSH Tunnel)

### Utilisation
```bash
# Pas besoin d'installation
ssh -R 80:localhost:8000 serveo.net
```

### Avantages
- ✅ Gratuit
- ✅ Pas besoin de compte
- ✅ URL personnalisable (avec compte gratuit)

### Inconvénients
- ⚠️ Nécessite SSH
- ⚠️ Peut être instable

---

## Comparaison rapide

| Solution | Installation | Gratuit | Stabilité | Vitesse |
|----------|--------------|---------|-----------|---------|
| **cloudflared** | ⚠️ brew | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **serveo** | ✅ SSH | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Scripts automatiques

### Script pour localtunnel
Crée `start-localtunnel.sh` :

```bash
#!/bin/bash
echo "🚀 Lancement de localtunnel..."
npx --yes localtunnel --port 8000
```

### Script pour cloudflared
Crée `start-cloudflared.sh` :

```bash
#!/bin/bash
echo "🚀 Lancement de cloudflared..."
cloudflared tunnel --url http://localhost:8000
```

---

## Recommandation

Je recommande **cloudflared** car :
- ✅ Pas de page d'avertissement
- ✅ Rapide et fiable
- ✅ Simple à utiliser
- ✅ Fonctionne immédiatement pour les webhooks

---

## Test rapide

Une fois le tunnel lancé, teste :

```bash
# Remplacer TON-URL par l'URL du tunnel
curl https://TON-URL/api/v1/health
```

---

## Configuration dans Skaleet

Une fois que tu as l'URL du tunnel, configure-la dans Skaleet comme endpoint webhook :

```
https://TON-URL/api/v1/webhooks/skaleet/card
```

