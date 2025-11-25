# 🔓 Tunnels sans page d'avertissement/mot de passe

## Problème avec localtunnel

Localtunnel affiche une page d'avertissement qui demande de cliquer sur "Click to Continue". C'est une mesure de sécurité.

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

## Autres solutions

### Option 1 : Utiliser localtunnel avec subdomain (si disponible)

```bash
npx --yes localtunnel --port 8000 --subdomain ton-nom-unique
```

⚠️ Les subdomains sont limités et peuvent ne pas être disponibles.

### Option 2 : Cliquer sur la page localtunnel

Quand localtunnel s'ouvre dans le navigateur :
1. Clique sur "Click to Continue"
2. L'URL fonctionnera ensuite

Mais cela ne fonctionne pas pour les webhooks automatiques.

### Option 3 : serveo (SSH tunnel)

```bash
ssh -R 80:localhost:8000 serveo.net
```

Pas de page d'avertissement, mais nécessite SSH.

---

## Comparaison

| Solution | Page d'avertissement | Installation | Gratuit |
|----------|---------------------|--------------|---------|
| **cloudflared** | ❌ Non | ⚠️ Oui | ✅ Oui |
| **localtunnel** | ✅ Oui | ❌ Non (npx) | ✅ Oui |
| **ngrok** | ❌ Non* | ⚠️ Oui | ✅ Oui* |
| **serveo** | ❌ Non | ✅ SSH | ✅ Oui |

*ngrok a des restrictions IP

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

