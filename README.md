# THW NOTFALL APP

Dieses Projekt ist eine einfache Webanwendung zur Verwaltung eines Notfall-Inventars biem THW. Ziel ist es, Notfallressourcen strukturiert zu erfassen, zu aktualisieren und zu verwalten.

## Technologien

- Backend: FastAPI (Python)
- Datenbank: MySQL (Aiven Cloud)
- Verbindung: mysql-connector-python
- Konfiguration: Umgebungsvariablen (.env)

## Projektstruktur

```
/backend
main.py
    /app
        routes/
        models/
        services/
    /db
        connection.py

/frontend
.env.example
requirements.txt
.gitignore
```

## Installation

### 1. Repository klonen

```bash
git clone <repo-url>
cd thw-notfall-app
```

### 2. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 3. Umgebung konfigurieren

`.env.example` kopieren und als `.env` speichern:

```
DB_HOST=...
DB_PORT=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```

## Anwendung starten

Backend starten mit:

```bash
uvicorn backend.main:app --reload
```

## Hinweise

- Die `.env` Datei wird nicht ins Repository hochgeladen.