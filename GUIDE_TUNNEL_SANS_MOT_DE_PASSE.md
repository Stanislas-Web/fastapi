# 🌐 Tunnels pour Card Connector

## Solution recommandée : cloudflared ⭐

**cloudflared** (Cloudflare Tunnel) est la meilleure alternative car :
- ✅ Pas de page d'avertissement
- ✅ Pas de mot de passe
- ✅ Rapide et fiable
- ✅ Gratuit

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

Ou utilise le script :
```bash
./start-cloudflared.sh
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

---

## Alternative : serveo (SSH tunnel)

```bash
ssh -R 80:localhost:8000 serveo.net
```

Pas de page d'avertissement, mais nécessite SSH.

---

## Comparaison

| Solution | Page d'avertissement | Installation | Gratuit |
|----------|---------------------|--------------|---------|
| **cloudflared** | ❌ Non | ⚠️ Oui | ✅ Oui |
| **serveo** | ❌ Non | ✅ SSH | ✅ Oui |

---

## Recommandation finale

**Utilise cloudflared** :
1. Installation simple : `brew install cloudflare/cloudflare/cloudflared`
2. Pas de page d'avertissement
3. Fonctionne immédiatement pour les webhooks
4. Rapide et fiable

---

## Installation rapide de cloudflared

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# Vérifier l'installation
cloudflared --version

# Lancer
cloudflared tunnel --url http://localhost:8000
```

---

## Test

Une fois cloudflared lancé, teste :

```bash
curl https://TON-URL.trycloudflare.com/api/v1/health
```

