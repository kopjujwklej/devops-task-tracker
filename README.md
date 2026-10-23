# DevOps Task Tracker

Prosta aplikacja do zarządzania zadaniami, zbudowana jako baza do nauki
praktycznych umiejętności DevOps: konteneryzacji, CI/CD, IaC, Kubernetesa,
monitoringu i bezpieczeństwa.

## Architektura

```
Frontend (HTML/CSS/JS) → Backend API (Flask) → PostgreSQL
```

## Status projektu

- [x] FAZA 1.1 — Kod źródłowy aplikacji
- [ ] FAZA 1.2 — Git / branching strategy
- [ ] FAZA 1.3 — Konteneryzacja (Docker)
- [ ] FAZA 2 — CI/CD
- [ ] FAZA 3 — Infrastruktura (Terraform)
- [ ] FAZA 4 — Kubernetes
- [ ] FAZA 5 — Observability
- [ ] FAZA 6 — Bezpieczeństwo

## Uruchomienie lokalne (bez Dockera — pełny setup w FAZIE 1.3)

Wymaga lokalnie zainstalowanego PostgreSQL.

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # uzupełnij DATABASE_URL swoimi danymi
flask --app app init-db    # tworzy tabelę tasks
python app.py               # backend na http://localhost:5000
```

Frontend to statyczne pliki — wystarczy otworzyć `frontend/index.html`
w przeglądarce (lub odpalić `python -m http.server` w folderze `frontend`).
