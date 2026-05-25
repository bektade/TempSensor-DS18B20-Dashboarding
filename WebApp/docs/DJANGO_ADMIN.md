# Django admin

Django admin is the staff UI for browsing and editing test data, import logs, and database records.

- URL: http://localhost:8000/admin/
- From another PC on the network: `http://<pi-ip>:8000/admin/` (see `make urls`)

## Default login

Credentials come from `WebApp/.env`:

| Setting | Purpose |
|---------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Login username (default `admin`) |
| `DJANGO_SUPERUSER_PASSWORD` | Login password |
| `DJANGO_SUPERUSER_EMAIL` | Email on the account (not used for login) |

The superuser is created on first `make startwebapp` if it does not exist yet.

## Main app vs Django admin (two different sites)

| Site | URL | Login required? |
|------|-----|-----------------|
| **Main app** (dashboard, charts, test list) | http://localhost:8000/ | **No** — open to anyone on the network |
| **Django admin** (database tables, import log) | http://localhost:8000/admin/ | **Yes** — username + password |

View-only users log in at **`/admin/`**, not at the home page. The home page has no login form.

## View-only (non-superuser) login

Use the same admin login page as the superuser:

1. Open http://localhost:8000/admin/ (or `http://<pi-ip>:8000/admin/`)
2. Enter the **view user’s username and password** (not the `admin` account unless you intend to use that)

### Requirements for a view-only user

In Django admin, a user can only sign in to `/admin/` if:

| Setting | View-only user | Superuser (`admin`) |
|---------|----------------|---------------------|
| **Active** | Yes | Yes |
| **Staff status** | **Yes** (required) | Yes |
| **Superuser status** | No | Yes |
| **Permissions** | View (read) on chosen models | All |

**Staff status** must be checked — without it, login fails even with a valid password.

### View-only vs edit access

| Permission | Can browse | Can edit existing records |
|------------|------------|---------------------------|
| **Can view …** only | Yes | No — form fields are read-only |
| **Can change …** | Yes | Yes |
| **Superuser** | Yes | Yes (all models) |

To let a staff user **edit** existing records (not just view):

1. Log in as `admin`
2. **Users** → select the user
3. Check **Staff status**
4. Under **User permissions**, add for each model you need:
   - *Can add …*
   - *Can change …*
   - *Can delete …* (optional)
5. Save

Or run from the project directory:

```bash
cd WebApp
docker compose exec django_web python manage.py grant_admin_edit_permissions USERNAME
```

### How to edit a record

1. Open http://localhost:8000/admin/
2. Click a model (e.g. **Product models**)
3. Click the **model name** (or TestID / serial) in the list — not only the checkbox
4. Change fields and click **Save**

Primary keys (`model_id`, `unit_id`, etc.) and **created at** timestamps are read-only; all other fields on that form are editable.

### Assign view permissions (as superuser)

1. Log in as `admin` at http://localhost:8000/admin/
2. **Authentication and Authorization** → **Users** → select the view user
3. Ensure **Staff status** is checked; **Superuser status** is unchecked
4. Under **User permissions**, add only **Can view …** for the models they should see (e.g. *Can view test run*, *Can view sensor reading*)
5. Save

That user then sees only those models in the admin sidebar and cannot add, change, or delete (unless you grant those permissions too).

### Reset a view user’s password

`make resetadmin` only updates the superuser from `.env`. For another user:

```bash
cd WebApp
docker compose exec django_web python manage.py changepassword THEIR_USERNAME
```

Or as superuser: **Users** → user → **Change password** form.

## Reset superuser (admin) password

If you forgot the password or cannot log in:

### 1. Choose a new password in `.env`

```bash
cd WebApp
nano .env
```

Set:

```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your_new_password_here
```

### 2. Apply the reset

```bash
make startwebapp    # if not already running
make resetadmin
```

This updates the existing admin user (or creates one if missing) to match `.env`.

### 3. Log in again

Open http://localhost:8000/admin/ and use the username and password from `.env`.

## Manual reset (without Make)

```bash
cd WebApp
docker compose exec django_web python manage.py changepassword admin
```

Interactive — prompts for a new password twice.

Or sync from `.env` directly:

```bash
./scripts/reset_django_admin.sh
```

## What you can do in admin

- **Test runs**, **sensor readings**, **import log**
- **Product models**, **product units**, **sensors**
- Filter and search test history

### Product model IDs after delete

PostgreSQL does **not** reset auto-increment IDs by itself. This app **does** resync the `model_id` sequence after each **Product model** delete in admin:

- Delete all models → the next new model gets **model_id = 1**
- Delete only some rows → the next ID is **max(existing model_id) + 1** (gaps are reused)

**Product units** use a separate `unit_id` sequence; deleting a model does not reset unit IDs.

You cannot delete a product model that still has units linked (`PROTECT`). Delete or reassign units first, then delete the model.

For charts and the public UI, use http://localhost:8000/ instead.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Forgot password (superuser `admin`) | `make resetadmin` after updating `.env` |
| View user cannot log in | Enable **Staff status** on that user |
| View user sees nothing | Add **Can view …** permissions for each model |
| Cannot edit records | User needs **Can change …** permissions, not view-only; or use `grant_admin_edit_permissions` |
| Blank / unstyled login page | Rebuild: `make stopWebApp && make startwebapp` |
| **403 Forbidden** on login | Use the same hostname as the main app (`localhost` or Pi IP, not mixed) |
| **Connection refused** | `make startwebapp` and `make status` — `sauna-django` must be Up |

More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## pgAdmin vs Django admin

| Tool | URL | Use for |
|------|-----|---------|
| Django admin | :8000/admin/ | App data, import log, editing records |
| pgAdmin | :5050/ | Raw SQL, schema inspection |

pgAdmin guide: [pgadmin/README.md](../pgadmin/README.md)
