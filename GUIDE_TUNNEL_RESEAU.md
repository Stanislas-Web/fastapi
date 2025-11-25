# 🔧 Résolution des problèmes de tunnel réseau

## Erreur cloudflared : "network is unreachable"

Si tu vois cette erreur :
```
ERR Failed to dial a quic connection error="failed to dial to edge with quic: write udp4 ... network is unreachable"
```

Cela signifie que cloudflared ne peut pas se connecter aux serveurs Cloudflare.

---

## Solutions

### Solution 1 : Vérifier la connexion Internet

```bash
# Tester la connexion
ping -c 3 8.8.8.8
curl -I https://www.cloudflare.com
```

Si ça ne fonctionne pas, vérifie ta connexion Internet.

---

### Solution 2 : Vérifier le firewall

Le firewall peut bloquer les connexions UDP nécessaires à cloudflared.

**Sur macOS** :
1. Va dans **Préférences Système** > **Sécurité** > **Pare-feu**
2. Vérifie que cloudflared est autorisé
3. Ou désactive temporairement le pare-feu pour tester

---

### Solution 3 : Utiliser un autre protocole

Essaie avec l'option `--protocol` :

```bash
cloudflared tunnel --url http://localhost:8000 --protocol http2
```

---

### Solution 4 : Utiliser serveo (SSH tunnel)

Si cloudflared ne fonctionne pas, utilise serveo qui utilise SSH :

```bash
ssh -R 80:localhost:8000 serveo.net
```

**Avantages** :
- ✅ Utilise SSH (port 22, généralement ouvert)
- ✅ Pas de problème de firewall UDP
- ✅ Simple et fiable

**Inconvénients** :
- ⚠️ Nécessite SSH installé
- ⚠️ URL change à chaque lancement

---

### Solution 5 : Utiliser localtunnel avec acceptation automatique

Si localtunnel fonctionne mais demande un mot de passe, tu peux :

1. **Lancer localtunnel**
2. **Ouvrir l'URL dans le navigateur**
3. **Cliquer sur "Click to Continue"**
4. **L'URL fonctionnera ensuite pour les webhooks**

Ou utilise un script pour automatiser :

```bash
# Lancer localtunnel
npx --yes localtunnel --port 8000 &
LT_PID=$!

# Attendre un peu
sleep 5

# Récupérer l'URL
URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
except:
    pass
")

echo "URL: $URL"
echo "Ouvre cette URL dans le navigateur et clique sur 'Click to Continue'"
```

---

### Solution 6 : Utiliser un VPN

Si tu es derrière un firewall strict, essaie avec un VPN :

1. Connecte-toi à un VPN
2. Relance cloudflared

---

## Comparaison des solutions

| Solution | Fiabilité | Installation | Firewall |
|----------|-----------|--------------|----------|
| **serveo** | ⭐⭐⭐⭐ | ✅ SSH | ✅ Fonctionne |
| **localtunnel** | ⭐⭐⭐ | ❌ Non | ✅ Fonctionne |
| **cloudflared** | ⭐⭐⭐⭐⭐ | ⚠️ Oui | ⚠️ Peut bloquer UDP |

---

## Recommandation

Si cloudflared ne fonctionne pas à cause du réseau :

**Utilise serveo** (SSH tunnel) :

```bash
ssh -R 80:localhost:8000 serveo.net
```

C'est la solution la plus fiable quand il y a des problèmes de firewall.

---

## Test de connectivité

Pour diagnostiquer le problème :

```bash
# Test 1: Connexion Internet
ping -c 3 8.8.8.8

# Test 2: Connexion HTTPS
curl -I https://www.cloudflare.com

# Test 3: Ports UDP (nécessaires pour cloudflared)
# Difficile à tester, mais si les autres fonctionnent, 
# c'est probablement un problème de firewall
```

---

## Alternative : Exposer directement (si possible)

Si tu es sur le même réseau que Skaleet ou si tu peux configurer un reverse proxy, tu peux exposer directement le service sans tunnel.

Mais pour les tests avec Skaleet, un tunnel est généralement nécessaire.

