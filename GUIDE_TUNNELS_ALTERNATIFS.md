# 🌐 Alternatives à ngrok - Tunnels pour Card Connector

## Problème avec ngrok

Si tu rencontres l'erreur `ERR_NGROK_9040`, c'est que ngrok bloque les connexions depuis ton IP. Voici des alternatives.

---

## Solution 1 : localtunnel (Recommandé) ⭐

### Installation
```bash
# Pas besoin d'installation, utilise npx
npx --yes localtunnel --port 8000
```

### Utilisation
```bash
# Lancer localtunnel
npx --yes localtunnel --port 8000
```

Cela affichera :
```
your url is: https://xxxx-xx-xx-xx-xx.loca.lt
```

### URL du webhook
```
https://xxxx-xx-xx-xx-xx.loca.lt/api/v1/webhooks/skaleet/card
```

### Avantages
- ✅ Gratuit
- ✅ Pas besoin de compte
- ✅ Pas de restriction IP
- ✅ Simple à utiliser

### Inconvénients
- ⚠️ URL change à chaque lancement
- ⚠️ Peut être plus lent que ngrok

---

## Solution 2 : cloudflared (Cloudflare Tunnel)

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

## Solution 3 : serveo (SSH Tunnel)

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

## Solution 4 : Pagekite

### Installation
```bash
pip install pagekite
```

### Utilisation
```bash
python -m pagekite.py 8000 xxxx.pagekite.me
```

---

## Comparaison rapide

| Solution | Installation | Gratuit | Stabilité | Vitesse |
|----------|--------------|---------|-----------|---------|
| **localtunnel** | ✅ npx | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |
| **cloudflared** | ⚠️ brew | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **ngrok** | ✅ brew | ✅* | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **serveo** | ✅ SSH | ✅ | ⭐⭐ | ⭐⭐⭐ |

*ngrok gratuit avec restrictions

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

Pour ton cas (erreur ngrok), je recommande **localtunnel** car :
- ✅ Pas besoin d'installation
- ✅ Fonctionne immédiatement
- ✅ Pas de restriction IP
- ✅ Simple à utiliser

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

