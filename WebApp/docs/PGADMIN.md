# pgAdmin (optional)

pgAdmin runs in a **separate Docker stack** so the main WebApp starts faster.

**Full guide:** [../pgadmin/README.md](../pgadmin/README.md)

```bash
cd WebApp
make startwebapp          # Postgres + Django first

cd pgadmin
make start                # optional DB browser
```

- URL: http://localhost:5050/
- Login: `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` in `WebApp/.env`
