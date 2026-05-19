# Custom visualizer (Plotly PNG)

A **presentation PNG** chart from the latest CSV — separate from Grafana. Uses Plotly with shared 90‑minute time axis, **Sauna Temp (°C)** and **Sauna Temp (°F)** subplots, bold labels, and grid lines.

**Source:** `Visualize/sensorDataVisualizer.py`  
**Output:** `Visualize/output/temp_reading_YYYY-MM-DD_HHMMAM.png` (same basename as the CSV, `.png` instead of `.csv`)

Grafana is unchanged; use this chart for slides and reports.

---

## Configuration (`.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `VISUALIZE_OUTPUT_DIR` | `Visualize/output` | Where PNG files are saved |
| `CSV_DIR` | `exports` | Where active CSV files are read |
| `TZ` | `America/Chicago` | Date/time in chart title — see [TIMEZONE.md](TIMEZONE.md) |

---

## Automatic PNG on stop

When you stop the stack, the publisher **stops reading**, builds the PNG from the latest CSV, then exits. The CSV is **not** archived on down (only on the next `docker compose up`).

**Recommended on the Pi** (plot on the host — most reliable):

```bash
cd ~/Projects/TempSensor
./scripts/compose-down.sh
```

Or plain `docker compose down` (plots inside the `mqtt-publisher` container after rebuild):

```bash
docker compose up -d --build --force-recreate mqtt-publisher
docker compose down
```

Example files:

```text
exports/temp_reading_2026-05-18_936PM.csv          # kept
Visualize/output/temp_reading_2026-05-18_936PM.png
```

---

## Refresh / reload the visualizer

Use this any time you want a **new PNG** from the latest CSV (no need to stop the stack).

### 1. One command (recommended)

Reads the newest `exports/temp_reading_*.csv`, writes a matching PNG:

```bash
cd ~/Projects/TempSensor
./scripts/plot_latest_csv.sh --presentation --output-auto
```

### 2. After editing `Visualize/sensorDataVisualizer.py`

Run the same command. **No Docker rebuild** needed for host-side plots.

### 3. After editing visualizer code used on `docker compose down`

Rebuild the publisher, then stop the stack:

```bash
cd ~/Projects/TempSensor
docker compose up -d --build --force-recreate mqtt-publisher
./scripts/compose-down.sh
```

### 4. Plot a specific CSV file

```bash
./scripts/plot_latest_csv.sh \
  --csv exports/temp_reading_2026-05-18_1032PM.csv \
  --presentation \
  -o Visualize/output/temp_reading_2026-05-18_1032PM.png
```

### 5. First-time setup (Python packages)

```bash
./scripts/firstTimeSetup.sh
./scripts/plot_latest_csv.sh --presentation --output-auto
```

Requires: `pandas`, `plotly`, `kaleido` (see `requirements.txt`).

### 6. View the latest PNG

```bash
ls -t Visualize/output/*.png | head -1
```

### Fix output folder permissions

If `Visualize/output/` is not writable (Docker created it as root):

```bash
sudo chown -R $USER:$USER Visualize/output
```

---

## Chart layout (reference)

| Feature | Setting |
|---------|---------|
| Title | Test date `MM/DD/YYYY` and generation time (e.g. `05/18/2026 \| 11:04 PM`) |
| X-axis | 90 minutes; labels at 15, 30, 45, 60, 75, 90 Min |
| X grid | Vertical lines every 5 min (50% opacity) |
| °C axis | 20–70°C; major ticks 10°C; minor ticks 5°C (marks only) |
| °F axis | 70–160°F; major ticks 20°F; minor ticks 10°F (marks only) |
| Y grid | Major dashed lines + 50% transparent intermediate grids |
| Legend | Top row, horizontal, next to the date title |

---

## Scripts

| Script | Use |
|--------|-----|
| `scripts/plot_latest_csv.sh` | Refresh PNG from latest CSV |
| `scripts/compose-down.sh` | Stop stack + plot latest CSV |
| `scripts/firstTimeSetup.sh` | Install host venv + dependencies |
