# pgAdmin for Product Test Data

pgAdmin is a **separate optional stack** for browsing and querying PostgreSQL. It is **not** started with `make startwebapp` so the main WebApp builds faster.

| Stack | What it runs | Start command |
|-------|----------------|---------------|
| **WebApp** | PostgreSQL + Django | `cd WebApp && make startwebapp` |
| **pgAdmin** | pgAdmin only | `cd WebApp/pgadmin && make start` |

## Quick start

### 1. Start PostgreSQL (required)

pgAdmin connects to the database published by the main WebApp stack:

```bash
cd WebApp
cp .env.example .env    # first time only
make startwebapp
```

PostgreSQL listens on host port **5433** by default (`POSTGRES_PUBLISH_PORT` in `.env`).

### 2. Start pgAdmin (optional)

```bash
cd WebApp/pgadmin
make start
```

Wait for **`pgAdmin is ready.`**, then open:

- On the Pi: http://localhost:5050/
- From another PC: `http://<pi-ip>:5050/` (run `make urls` for the address)

### 3. Log in to pgAdmin

Credentials from `WebApp/.env`:

| Setting | Variable |
|---------|----------|
| Email | `PGADMIN_DEFAULT_EMAIL` |
| Password | `PGADMIN_DEFAULT_PASSWORD` |

Default example:

```
PGADMIN_DEFAULT_EMAIL=pgadmin@tempsensor.com
PGADMIN_DEFAULT_PASSWORD=change_me_pgadmin
```

## Pre-registered server

Each `make start` registers **Product Test DB** automatically.

```
Servers
  └── Servers
        └── Product Test DB
              └── Databases
                    └── sauna_tests
                          └── Schemas → public → Tables
```

| Setting | Value |
|---------|--------|
| Host | `host.docker.internal` (default) |
| Port | `5433` (host port from `POSTGRES_PUBLISH_PORT`) |
| Database | `POSTGRES_DB` (default `sauna_tests`) |
| Username | `POSTGRES_USER` (default `sauna_user`) |
| Password | `POSTGRES_PASSWORD` in `.env` |

pgAdmin runs in its own container and reaches PostgreSQL through the **host-published port**, not the internal Docker service name `postgres`.

### Override connection host/port

In `WebApp/.env`:

```
PGADMIN_POSTGRES_HOST=host.docker.internal
PGADMIN_POSTGRES_PORT=5433
```

Use these if PostgreSQL runs on another machine or port.

## Makefile targets

Run from `WebApp/pgadmin/`:

| Command | Action |
|---------|--------|
| `make start` | Start pgAdmin (checks Postgres is running) |
| `make stop` | Stop pgAdmin only |
| `make restart` | Restart pgAdmin |
| `make logs` | Follow container logs |
| `make status` | Container status |
| `make reset` | Remove container and pgAdmin data volume |
| `make urls` | Show login URL |

## Browse test data

| Table | Contents |
|-------|----------|
| `product_models` | Product model names, supplier, specs |
| `product_units` | Orders (serial numbers) |
| `test_runs` | Test sessions (TestID = `test_run_id`) |
| `sensors` | Sensor serials and labels |
| `sensor_readings` | Temperature time series |
| `import_log` | CSV import history |
| `powerbox_types` | Power box types (Lee, Luis, Wang) |

### Example query

```sql
SELECT tr.test_run_id AS "TestID",
       pm.model_name,
       pu.serial_number,
       tr.test_date,
       tr.tester_name
FROM test_runs tr
JOIN product_units pu ON pu.unit_id = tr.unit_id
JOIN product_models pm ON pm.model_id = pu.model_id
ORDER BY tr.test_date DESC
LIMIT 20;
```

More SQL: [../docs/DATABASE.md](../docs/DATABASE.md)

## pgAdmin vs Django admin

| Tool | URL | Best for |
|------|-----|----------|
| Django app | :8000/ | Dashboard, tests, imports |
| Django admin | :8000/admin/ | Editing records |
| pgAdmin | :5050/ | Raw SQL, schema inspection |

Django admin credentials are separate — see [../docs/DJANGO_ADMIN.md](../docs/DJANGO_ADMIN.md).

## Stop pgAdmin

```bash
cd WebApp/pgadmin
make stop
```

This does **not** stop PostgreSQL or Django. To stop the whole WebApp:

```bash
cd WebApp
make stopWebApp
```

## Reset pgAdmin

Use if login is stuck on an old password or the server list is wrong:

```bash
cd WebApp/pgadmin
make reset
make start
```

## Troubleshooting

```bash
cd WebApp/pgadmin
make status
make logs
```

| Issue | Fix |
|-------|-----|
| `PostgreSQL is not running` | `cd .. && make startwebapp` first |
| pgAdmin page blank / empty response | Wait 30–90s after `make start`, then refresh |
| `password authentication failed` | Match `POSTGRES_PASSWORD` in `../.env` |
| Cannot connect to server | Host must be `host.docker.internal`, port **5433** (not 5432) |
| Port 5050 in use | Set `PGADMIN_PUBLISH_PORT=5051` in `../.env` and restart |
| Server missing in tree | `make reset && make start` |

### Manual server registration

If **Product Test DB** is missing:

1. Right-click **Servers** → **Register** → **Server…**
2. **General** → Name: `Product Test DB`
3. **Connection**:
   - Host: `host.docker.internal` (or Pi LAN IP from another PC’s pgAdmin install)
   - Port: `5433`
   - Database: `sauna_tests`
   - Username: `sauna_user`
   - Password: from `POSTGRES_PASSWORD` in `.env`

## Files in this directory

| File | Purpose |
|------|---------|
| `docker-compose.yml` | pgAdmin container only |
| `entrypoint.sh` | Auto-register Postgres server from `.env` |
| `Makefile` | start / stop / logs / reset |
| `README.md` | This guide |

Credentials and Postgres settings live in the parent `WebApp/.env` file.
