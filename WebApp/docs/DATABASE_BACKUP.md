# Database backup and restore

PostgreSQL data **does not live inside the Django Docker image**. It is stored in a Docker volume named **`postgres_data`**.

| What | Survives `make rebuildwebapp-hub`? | Survives `make stopWebApp`? | Survives new machine / fresh clone? |
|------|--------------------------------------|-------------------------------|-------------------------------------|
| PostgreSQL data (`postgres_data` volume) | Yes | Yes | **No** — unless you backup/restore |
| CSV import folders (`data/import_pending/`, `data/archive/`) | Yes | Yes | Yes — if you copy the `WebApp/` folder |

Pulling a new Hub image only replaces the **django** container. Postgres keeps running with the same volume.

---

## Backup (keep a copy)

```bash
cd WebApp
make db-backup
```

Creates a compressed dump under `data/backups/`, for example:

`data/backups/sauna_tests_20260518_143022.sql.gz`

Copy that file somewhere safe (USB drive, cloud, another PC).

---

## Restore on this machine

Postgres must be running (`make startwebapp` or `make startwebapp-hub`).

```bash
cd WebApp
make db-restore FILE=data/backups/sauna_tests_20260518_143022.sql.gz
```

Use the same `POSTGRES_PASSWORD` in `.env` as when the backup was taken (or the restore will fail to connect).

---

## New machine: clone repo + run from Docker Hub + restore data

**1. Clone and configure**

```bash
git clone <repo-url> TempSensor
cd TempSensor/WebApp
cp .env.example .env    # set POSTGRES_PASSWORD, DJANGO_SECRET_KEY, etc.
```

**2. Start empty stack from Hub**

```bash
make startwebapp-hub
make migrate            # apply any new schema changes
```

**3. Copy backup file into place**

```bash
mkdir -p data/backups
cp /path/to/sauna_tests_YYYYMMDD_HHMMSS.sql.gz data/backups/
```

**4. Restore**

```bash
make db-restore FILE=data/backups/sauna_tests_YYYYMMDD_HHMMSS.sql.gz
```

**5. (Optional) Copy CSV archives**

If you use CSV import, also copy `data/import_pending/` and `data/archive/` from the old machine.

Open http://localhost:8000/ — your test data should be back.

---

## What deletes the database

These **remove** the `postgres_data` volume and all rows:

```bash
docker compose down -v
docker volume rm webapp_postgres_data    # exact name: docker volume ls
```

`make stopWebApp` alone is safe — it does **not** use `-v`.

---

## Manual backup (without Make)

```bash
cd WebApp
mkdir -p data/backups
docker compose exec -T postgres pg_dump -U sauna_user -d sauna_tests \
  | gzip > data/backups/sauna_tests_manual.sql.gz
```

See also: [DATABASE.md](DATABASE.md) · [DOCKER_HUB.md](DOCKER_HUB.md)
