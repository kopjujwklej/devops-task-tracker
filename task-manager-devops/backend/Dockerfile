# ============================================================
# STAGE 1: builder — instalujemy zależności w izolowanym etapie
# ============================================================
# 🔴 MUST KNOW: multi-stage build pozwala mieć w finalnym obrazie
# TYLKO to, co potrzebne do uruchomienia appki — bez kompilatorów,
# cache'u pip i innych śmieci potrzebnych wyłącznie do budowania.
FROM python:3.12-slim AS builder

WORKDIR /app

# Kopiujemy TYLKO requirements.txt najpierw — klucz do cache'owania warstw.
# Jeśli nie zmienisz zależności, Docker weźmie tę warstwę z cache
# i pominie cały "pip install" (oszczędność nawet kilku minut na buildzie).
COPY requirements.txt .

# --user instaluje pakiety do ~/.local, co ułatwia kopiowanie do kolejnego stage'a
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================
# STAGE 2: runtime — finalny, lekki obraz bez narzędzi budowania
# ============================================================
FROM python:3.12-slim

WORKDIR /app

# 🔴 MUST KNOW: nigdy nie uruchamiamy procesu w kontenerze jako root.
# Jeśli ktoś przejmie proces, zwykły użytkownik ogranicza szkody
# dużo skuteczniej niż root.
RUN useradd --create-home --shell /bin/bash appuser

# Kopiujemy TYLKO zainstalowane zależności z poprzedniego etapu
# (bez pip cache, bez kompilatorów — stąd mniejszy obraz finalny)
COPY --from=builder /root/.local /home/appuser/.local

# Kod aplikacji kopiujemy na końcu — zmienia się najczęściej,
# więc umieszczamy to jak najpóźniej, by nie unieważniać cache'u wcześniejszych warstw
COPY . .

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 5000

# 🔴 MUST KNOW: HEALTHCHECK pozwala samemu Dockerowi/docker-compose wiedzieć,
# czy kontener faktycznie działa poprawnie — nie tylko czy proces żyje.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# 🟡 NICE TO KNOW: gunicorn zamiast wbudowanego serwera Flaska —
# serwer deweloperski Flaska nie jest przystosowany do produkcji
# (jeden wątek, brak odporności na awarie).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
