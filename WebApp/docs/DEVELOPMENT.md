# Development (host)

Docker (`make startwebapp`) installs dependencies inside the `django_web` image. Use a **separate host venv** only when running Django commands outside Docker.

## Virtual environments

| Path | Purpose |
|------|---------|
| `SensorDataCollector/venv/` | Collector stack: MQTT publisher, Plotly visualizer |
| `WebApp/.venv/` | Django + psycopg2 |

Do not mix them — dependency versions will conflict.

## One-time setup

```bash
cd WebApp
./scripts/setup_venv.sh
cp .env.example .env
```

For host tools against Docker Postgres:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

Start Postgres only:

```bash
make startwebapp   # or: docker compose up -d postgres
```

## Host commands

```bash
cd WebApp
source scripts/activate_venv.sh
make migrate
python manage.py import_pending_csv
python manage.py createsuperuser
```

Or migrate + dev server:

```bash
./scripts/run_dev.sh
```

## Django superuser (Docker)

```bash
docker compose exec django_web python manage.py createsuperuser
```

Or set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, and `DJANGO_SUPERUSER_EMAIL` in `.env` before `make startwebapp`.
