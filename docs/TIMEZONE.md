# Timezone (Chicago / CDT)

If timestamps look **5 hours ahead** (UTC instead of local), set the Raspberry Pi and Docker stack to Chicago time.

## Set Pi clock and timezone

From the project root:

```bash
cd ~/Projects/TempSensor
sudo ./scripts/setup_timezone.sh
```

This sets **America/Chicago** (CDT in summer, CST in winter) and enables **NTP** internet time sync.

## Apply to the stack

Add to `.env` (see `.env.example`):

```env
TZ=America/Chicago
```

Recreate services that display or log local time:

```bash
docker compose up -d --force-recreate mqtt-publisher grafana
```

## Verify

```bash
timedatectl
date
docker compose logs mqtt-publisher --tail 3
```

CSV timestamps and Grafana should match local Chicago time after this.
