"""
DevOps Task Tracker — Backend API
===================================
Prosty REST API do zarządzania zadaniami (CRUD).
Zbudowany we Flasku, żeby na start było jak najprościej,
ale z zachowaniem dobrych praktyk: config przez ENV,
health-checki, separacja modelu od logiki.
"""

import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# --- KONFIGURACJA APLIKACJI -------------------------------------------

app = Flask(__name__)

# 🔴 MUST KNOW: w DevOps NIGDY nie zaszywamy configów (haseł, adresów baz)
# na sztywno w kodzie. Bierzemy je ze zmiennych środowiskowych (ENV).
# Dzięki temu TEN SAM obraz Dockera można uruchomić na dev/staging/prod
# bez zmiany ani jednej linijki kodu — zmieniają się tylko env vary.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://taskuser:taskpass@localhost:5432/taskdb",  # fallback na lokalny dev
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# CORS pozwala frontendowi (inny port/origin) rozmawiać z tym API.
CORS(app)


# --- MODEL DANYCH -------------------------------------------------------

class Task(db.Model):
    """Pojedyncze zadanie w naszym task-managerze."""

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default="medium")  # low / medium / high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Zamienia obiekt Pythona na słownik -> JSON dla frontendu."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_done": self.is_done,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


# --- HEALTH CHECKS (kluczowe dla DevOps!) -------------------------------

@app.route("/health")
def health():
    """
    🔴 MUST KNOW: Liveness probe.
    Odpowiada na pytanie: "czy proces aplikacji w ogóle żyje?"
    Orkiestrator (K8s) restartuje kontener, jeśli to nie odpowiada.
    Celowo NIE sprawdzamy tu bazy danych — to osobna odpowiedzialność.
    """
    return jsonify({"status": "ok"}), 200


@app.route("/ready")
def ready():
    """
    🔴 MUST KNOW: Readiness probe.
    Odpowiada na pytanie: "czy aplikacja jest gotowa przyjmować ruch?"
    Tutaj SPRAWDZAMY połączenie z bazą — jeśli baza padła,
    load balancer nie powinien kierować tu żadnych requestów.
    """
    try:
        db.session.execute(db.select(1))
        return jsonify({"status": "ready", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "not ready", "error": str(e)}), 503


# --- ENDPOINTY BIZNESOWE (CRUD) ------------------------------------------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Zwraca listę wszystkich zadań, najnowsze pierwsze."""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Tworzy nowe zadanie."""
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    # 🟡 NICE TO KNOW: walidacja wejścia to podstawa bezpieczeństwa (input validation)
    if not title:
        return jsonify({"error": "Pole 'title' jest wymagane"}), 400

    priority = data.get("priority", "medium")
    if priority not in ("low", "medium", "high"):
        return jsonify({"error": "Pole 'priority' musi być: low, medium lub high"}), 400

    task = Task(title=title, description=data.get("description", ""), priority=priority)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Aktualizuje zadanie (np. oznacza jako wykonane)."""
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Zadanie nie istnieje"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "is_done" in data:
        task.is_done = bool(data["is_done"])

    db.session.commit()
    return jsonify(task.to_dict()), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Usuwa zadanie."""
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Zadanie nie istnieje"}), 404

    db.session.delete(task)
    db.session.commit()
    return "", 204


# --- INICJALIZACJA BAZY (tylko na potrzeby dev/nauki) ---------------------

@app.cli.command("init-db")
def init_db():
    """
    Komenda: `flask init-db`
    🟡 NICE TO KNOW: w prawdziwym projekcie migracje robi się narzędziem
    typu Alembic/Flask-Migrate, a nie create_all(). Tu upraszczamy,
    żeby skupić się na DevOps, a nie na niuansach ORM.
    """
    with app.app_context():
        db.create_all()
        print("Baza danych zainicjalizowana ✅")


if __name__ == "__main__":
    # 🔴 MUST KNOW: debug=True NIGDY na produkcji (ujawnia stack trace,
    # pozwala na zdalne wykonanie kodu). Sterujemy tym przez ENV.
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
