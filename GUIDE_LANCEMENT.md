# 🚀 Guide de Lancement - Card Connector

## Méthode 1 : Avec Docker Compose (Recommandé) ⭐

C'est la méthode la plus simple car elle lance automatiquement PostgreSQL et le service.

### Prérequis
- Docker et Docker Compose installés

### Étapes

1. **Vérifier que Docker est installé** :
```bash
docker --version
docker compose version
```

2. **Configurer le fichier `.env`** :
```bash
# Copier l'exemple si tu n'as pas encore de .env
cp .env.example .env

# Éditer le .env avec tes valeurs (ou garder les valeurs par défaut pour les tests)
# Important : pour utiliser les données mockées, ajoute :
NI_USE_MOCK=true
```

3. **Lancer les services** :
```bash
docker compose up -d
```

Cette commande lance :
- PostgreSQL sur le port 5432
- Card Connector sur le port 8000

4. **Appliquer les migrations** :
```bash
docker compose exec card-connector alembic upgrade head
```

5. **Vérifier que tout fonctionne** :
```bash
curl http://localhost:8000/api/v1/health
```

6. **Voir les logs** :
```bash
docker compose logs -f card-connector
```

7. **Arrêter les services** :
```bash
docker compose down
```

---

## Méthode 2 : Lancement Local (Sans Docker)

### Prérequis
- Python 3.12+
- PostgreSQL 15+ installé et lancé
- Environnement virtuel Python

### Étapes

1. **Créer et activer l'environnement virtuel** :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Configurer PostgreSQL** :
```bash
# Créer l'utilisateur et la base de données
psql -U postgres

# Dans psql :
CREATE USER carduser WITH PASSWORD 'cardpass';
CREATE DATABASE card_connector_db OWNER carduser;
\q
```

4. **Configurer le fichier `.env`** :
```bash
# Vérifier que ton .env contient :
DATABASE_URL=postgresql+asyncpg://carduser:cardpass@localhost:5432/card_connector_db
NI_USE_MOCK=true  # Pour utiliser les données mockées
```

5. **Appliquer les migrations** :
```bash
alembic upgrade head
```

6. **Lancer le service** :
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Le service sera accessible sur : http://localhost:8000

---

## Méthode 3 : Lancement Local (Sans PostgreSQL)

Si tu veux juste tester les endpoints sans base de données :

1. **Activer l'environnement virtuel** :
```bash
source venv/bin/activate
```

2. **Configurer le `.env`** :
```bash
# Ajouter dans .env :
NI_USE_MOCK=true
# La DATABASE_URL peut être incorrecte, le service démarrera quand même
```

3. **Lancer le service** :
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

⚠️ **Note** : Les webhooks nécessitant la base de données ne fonctionneront pas, mais tu peux tester :
- `/api/v1/health` ✅
- `/docs` (documentation API) ✅

---

## Vérification du Service

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Réponse attendue :
```json
{
  "status": "ok"
}
```

### 2. Documentation API
Ouvre dans ton navigateur :
```
http://localhost:8000/docs
```

### 3. Tester un Webhook
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/skaleet/card \
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

## Configuration du Mode Mock

Pour utiliser les données mockées (sans appeler de vrais services) :

Dans ton fichier `.env`, ajoute :
```bash
NI_USE_MOCK=true
```

Avec ce mode :
- ✅ Les appels à NI retournent des données mockées
- ✅ Les numéros VISA sont générés automatiquement
- ✅ Pas besoin de vrais services externes

---

## Dépannage

### Port 8000 déjà utilisé
```bash
# Trouver le processus
lsof -ti:8000

# Arrêter le processus
kill $(lsof -ti:8000)

# Ou utiliser un autre port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Erreur de connexion à la base de données
- Vérifie que PostgreSQL est lancé : `pg_isready`
- Vérifie les credentials dans `.env`
- Vérifie que la base de données existe

### Dépendances manquantes
```bash
pip install -r requirements.txt
# Si greenlet manque :
pip install greenlet
```

### Erreur "Module not found"
Assure-toi d'être dans l'environnement virtuel :
```bash
source venv/bin/activate
```

---

## Commandes Utiles

### Voir les logs en temps réel
```bash
# Avec Docker
docker compose logs -f card-connector

# Sans Docker (si lancé en arrière-plan)
tail -f /tmp/card-connector.log
```

### Arrêter le service
```bash
# Avec Docker
docker compose down

# Sans Docker
pkill -f "uvicorn app.main:app"
```

### Relancer après modification du code
Le mode `--reload` relance automatiquement. Sinon :
```bash
# Arrêter puis relancer
pkill -f "uvicorn"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## URLs Importantes

Une fois le service lancé :

- **Health Check** : http://localhost:8000/api/v1/health
- **Documentation API** : http://localhost:8000/docs
- **Webhook Skaleet** : http://localhost:8000/api/v1/webhooks/skaleet/card

---

## Prochaines Étapes

1. ✅ Service lancé
2. 📝 Tester les endpoints via `/docs`
3. 🔔 Configurer ngrok pour recevoir des webhooks Skaleet
4. 🧪 Tester avec les cartes mockées (voir `CARTES_TEST.md`)

---

## Besoin d'aide ?

- Vérifie les logs pour les erreurs
- Consulte `README.md` pour plus de détails
- Vérifie que toutes les variables d'environnement sont configurées dans `.env`

