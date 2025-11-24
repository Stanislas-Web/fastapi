FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système
# gcc est nécessaire pour compiler asyncpg et autres packages avec extensions C
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 8000

# Commande pour lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

