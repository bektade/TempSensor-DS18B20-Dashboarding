# WebApp troubleshooting

## ERR_CONNECTION_REFUSED on http://localhost:8000/

Nothing is listening on port 8000 **on the machine where your browser runs**.

### Case A: Browser on your PC, app runs on the Raspberry Pi

`localhost` on the PC is your PC, not the Pi.

```bash
# On the Pi (SSH):
cd ~/Projects/TempSensor/WebApp
make startwebapp
make urls
```

Open the **LAN** URL, for example:

`http://192.168.0.198:8000/`

(Your IP is shown by `make urls` or `hostname -I` on the Pi.)

### Case B: Browser on the Pi itself

Start the stack:

```bash
cd ~/Projects/TempSensor/WebApp
make startwebapp
make status
```

`sauna-django` must show **Up**. Then open http://localhost:8000/

### Quick checks

```bash
cd WebApp
make status
make urls
curl -sI http://127.0.0.1:8000/
docker logs sauna-django --tail 30
```

| `make status` | Action |
|---------------|--------|
| No `sauna-django` / not Up | `make startwebapp` |
| `curl` returns 200 | App is fine — fix the URL you use in the browser |
| `curl` fails | `docker logs sauna-django` |

## ERR_EMPTY_RESPONSE on pgAdmin (:5050)

pgAdmin is still starting. Wait for `pgAdmin is ready.` from `cd pgadmin && make start`, then refresh. See [pgadmin/README.md](../pgadmin/README.md).

## Django admin blank or login fails

Login from `.env`:

- Username: `DJANGO_SUPERUSER_USERNAME` (default `admin`)
- Password: `DJANGO_SUPERUSER_PASSWORD`

**Forgot password / locked out:** see [DJANGO_ADMIN.md](DJANGO_ADMIN.md) or run:

```bash
cd WebApp
# Set DJANGO_SUPERUSER_PASSWORD=your_new_password in .env
make resetadmin
```

Then open http://localhost:8000/admin/ (or `http://<pi-ip>:8000/admin/` from another PC).

If the page looks unstyled or login returns **403 Forbidden**, rebuild Django:

```bash
make stopWebApp
make startwebapp
```

## HTTP 400 / “Disallowed Host”

Use the LAN IP URL after `make startwebapp`, or ensure `DJANGO_DEBUG=1` in `.env` and rebuild:

```bash
make stopWebApp
make startwebapp
```
