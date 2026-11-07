# IND320 — Oblig 3

**Report + complete step-by-step guide**

| | |
|---|---|
| Repo | `Code/IND320/IND320LjosNorth` |
| Branch | `Dev` ✅ |
| Date | 2026-11-07 |
| Assumption | **Oblig 3 has not been started.** Zero analysis code, zero weather pages, zero weather data in MongoDB. This document is the plan from a clean slate. |

> **How to read this:** §1–§3 is the overview. §5 is the important part — a detailed, copy-paste guide to getting every API into Python. §6–§7 are the notebook and Streamlit build guides. §10 is the final checklist.

---

## Contents

1. [TL;DR — the task in 10 lines](#1-tldr--the-task-in-10-lines)
2. [Where the project stands](#2-where-the-project-stands)
3. [Deliverables checklist](#3-deliverables-checklist)
4. [Before you code (30 minutes)](#4-before-you-code-30-minutes)
5. [**Deep dive: getting the APIs into Python**](#5-deep-dive-getting-the-apis-into-python)
   - [5.1 NVE Magasinstatistikk](#51-nve-magasinstatistikk)
   - [5.2 open-meteo ERA5](#52-open-meteo-era5-the-big-one)
   - [5.3 NVE geodata / shapefiles](#53-nve-geodata--shapefiles)
   - [5.4 MongoDB](#54-mongodb-upload--read)
6. [Notebook — build guide](#6-notebook--build-guide)
7. [Streamlit — build guide](#7-streamlit--build-guide)
8. [Run order (copy-paste)](#8-run-order-copy-paste)
9. [Troubleshooting](#9-troubleshooting)
10. [Final hand-in checklist](#10-final-hand-in-checklist)
11. [Time estimate](#11-time-estimate)

---

## 1. TL;DR — the task in 10 lines

1. The Streamlit app already works (Oblig 1 + 2). Oblig 3 **adds** weather data and four analyses.
2. Three data sources: **NVE Magasinstatistikk** (already loaded), **open-meteo ERA5** (new), **NVE geodata** (new).
3. Download NVE region polygons, sample **1 000 random points per region**, download hourly ERA5 for 2024 for those points.
4. Aggregate the points to **one average series per region** — never store 1 000 raw series per region.
5. Upload the aggregated weather to **MongoDB** so the app stays fast.
6. Notebook: precipitation plot with **DCT + SPC outliers**, temperature plot with **LOF anomalies**.
7. Notebook: **STL** decomposition and **spectrogram** of `filled degree`.
8. App: new **Meteorological data** page, a **STL / Spectrogram** tabbed page, a **SPC / LOF** tabbed page.
9. Reorder pages logically; keep `Dev` clean.
10. Finish with the 300–500 word log, AI section, PDF export, and a 5-minute screencast.

---

## 2. Where the project stands

### ✅ What already works (verified)

| Thing | State |
|---|---|
| Branch | `Dev`, clean start for Oblig 3 |
| App | 5 pages: Home, Reservoir tables, Reservoir plots, Transmission plots, Settings |
| NVE API | `utils/dataLoaders.py` → `load_magazine_data_api()` works (14 949 rows, 1995 → today) |
| MongoDB | ENTSO-E transmission data works (70 072 docs) |
| Environment | Python 3.12.15, streamlit 1.61.1, pandas 3.0.5, numpy 2.5.2, plotly 6.9.0, statsmodels 0.14.6, scipy 1.18.0, scikit-learn 1.9.0 |
| App tests | All pages run without exceptions |

### ❌ What Oblig 3 still needs

| Missing piece | Where it will live |
|---|---|
| Shapefile download + 1 000-point sampling | notebook + `data/regions/` |
| open-meteo download function | `utils/meteo.py` (new) |
| Weather data in MongoDB | `meteo` database |
| DCT / SPC / LOF / STL / spectrogram functions | `utils/analysis.py` (new) |
| Meteorological data page | `pages/meteorologicalData.py` (new) |
| STL + Spectrogram page | `pages/reservoirAnalysis.py` (new) |
| SPC + LOF page | `pages/weatherAnalysis.py` (new) |
| Notebook narrative, log, AI section, PDF | `notebooks/Oblig3.ipynb` |
| 5-minute screencast | `Oblig/Oblig3/` + link in notebook |

**Important:** the notebook currently contains only links; treat it as a blank template. Do not build on it until §6.

---

## 3. Deliverables checklist

### Notebook
- [ ] Clear, navigable headings
- [ ] All code blocks commented and reproducible
- [ ] Every cell executed before PDF export (outputs visible)
- [ ] Brief **AI usage** description
- [ ] **300–500 word log** of the compulsory work
- [ ] Links to GitHub repo + Streamlit app
- [ ] `.ipynb` committed to the repo

### Streamlit app
- [ ] Meteorological data (selector-driven, with download control)
- [ ] Page with `st.tabs()` → **STL** | **Spectrogram**
- [ ] Page with `st.tabs()` → **Outlier/SPC** | **Anomaly/LOF**
- [ ] Pages reordered logically
- [ ] App still runs online with MongoDB + APIs

### Screencast
- [ ] ~5 minutes
- [ ] Shows the running app + explains the code
- [ ] Link open to everyone (or video in repo)

---

## 4. Before you code (30 minutes)

### 4.1 Branch

You are on `Dev` — correct place to start. The task also says to use a temporary branch until peer review 2. If you follow that literally:

```bash
cd Code/IND320/IND320LjosNorth
git switch -c oblig3        # branch from Dev
git push -u origin oblig3
# ... work ...
# after peer review 2 + feedback 2:
git switch main
git merge oblig3
```

If the course allows working directly on `Dev`, stay on `Dev`. Either way, **do not push Oblig 3 directly to `main` before the review**.

### 4.2 Dependencies

`geopandas` is missing (needed for shapefiles). `scipy` is installed but only indirectly, so add it explicitly:

```bash
cd Code/IND320/IND320LjosNorth
uv add scipy geopandas pyarrow
uv sync
```

`pyarrow` is for parquet caching; it is already installed but harmless to add.

### 4.3 Files you will create

```
utils/
  meteo.py            # NEW: region points, open-meteo, Mongo read/write
  analysis.py         # NEW: DCT/SPC, LOF, STL, spectrogram
pages/
  meteorologicalData.py   # NEW
  reservoirAnalysis.py    # NEW (STL + Spectrogram tabs)
  weatherAnalysis.py      # NEW (SPC + LOF tabs)
data/
  regions/
    NVE_Region.geojson    # downloaded polygons
    points_<region>.csv   # 1 000 sampled points per region
```

### 4.4 Secrets

Already handled: `.streamlit/secrets.toml` and `no_sync/` are git-ignored. Never commit them. The weather upload uses the same MongoDB credentials as the transmission data.

---

## 5. Deep dive: getting the APIs into Python

### Overview

| Source | URL | Auth | Returns | Already used? |
|---|---|---|---|---|
| NVE Magasinstatistikk | `https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData` | none | weekly reservoir filling, 1995→now | ✅ yes |
| open-meteo ERA5 | `https://archive-api.open-meteo.com/v1/archive` | none | hourly historical weather | ❌ new |
| NVE geodata (regions) | `https://kart.nve.no/enterprise/rest/services/Mapservices/Administrasjon2/MapServer/0/query` | none | polygons RS/RØ/RV/RM/RN | ❌ new |
| MongoDB Atlas | `mongodb+srv://...` | user/password in `secrets.toml` | storage for app | ✅ yes |

---

### 5.1 NVE Magasinstatistikk

#### What it is

One GET request returns the **entire** reservoir statistics dataset as JSON. There are **no date or area parameters** — the endpoint always returns everything. You filter in pandas.

- ~4 MB, ~15 000 rows
- One row per **week** × **area**
- Areas: `EL` 1–5 (price areas NO1–NO5), `NO` 0 (whole country), `VASS` 1–3 (watercourse areas)
- Dates: 1995 → today

#### Step 1 — make the request

```python
import requests
import pandas as pd

MAGASIN_URL = (
    "https://biapi.nve.no/magasinstatistikk/api/"
    "Magasinstatistikk/HentOffentligData"
)

response = requests.get(MAGASIN_URL, timeout=120)
response.raise_for_status()          # crash loudly on 4xx/5xx
rows = response.json()               # list[dict]
print(type(rows), len(rows))         # <class 'list'> 14949
```

#### Step 2 — JSON → DataFrame

```python
df = pd.DataFrame(rows)
print(df.columns.tolist())
print(df.iloc[0])
```

Raw columns:

| API column | Meaning |
|---|---|
| `dato_Id` | date (ISO string) |
| `omrType` | `EL`, `NO`, `VASS` |
| `omrnr` | area number |
| `iso_aar` / `iso_uke` | ISO year / week |
| `fyllingsgrad` | filling degree, 0–1 |
| `kapasitet_TWh` | capacity |
| `fylling_TWh` | stored energy |
| `neste_Publiseringsdato` | next publication (ISO string) |
| `fyllingsgrad_forrige_uke` | filling degree last week |
| `endring_fyllingsgrad` | change in filling degree |

#### Step 3 — rename, parse, filter

```python
RENAME = {
    "dato_Id": "date",
    "iso_aar": "year",
    "iso_uke": "week",
    "fyllingsgrad": "filled_degree",
    "kapasitet_TWh": "capacity_TWh",
    "fylling_TWh": "filled_TWh",
    "neste_Publiseringsdato": "next_publication",
    "fyllingsgrad_forrige_uke": "filled_degree_last_week",
    "endring_fyllingsgrad": "change_filled_degree",
}

df = df.rename(columns=RENAME)
df["date"] = pd.to_datetime(df["date"])
```

#### Step 4 — complete loader

```python
def load_magasinstatistikk(area_type=None, area_nr=None, start=None, end=None):
    """Download NVE reservoir data and optionally filter area and dates."""
    response = requests.get(MAGASIN_URL, timeout=120)
    response.raise_for_status()

    df = pd.DataFrame(response.json()).rename(columns=RENAME)
    df["date"] = pd.to_datetime(df["date"])

    if area_type is not None:
        df = df[df["omrType"] == area_type]
    if area_nr is not None:
        df = df[df["omrnr"] == area_nr]
    if start is not None:
        df = df[df["date"] >= pd.Timestamp(start)]
    if end is not None:
        df = df[df["date"] <= pd.Timestamp(end)]

    return df.sort_values("date").reset_index(drop=True)


# example: NO3 in 2024
no3 = load_magasinstatistikk("EL", 3, "2024-01-01", "2024-12-31")
print(no3.shape)       # (52, 11)
print(no3.head())
```

#### Step 5 — verify it worked

```python
assert len(no3) == 52
assert no3["date"].min() >= pd.Timestamp("2024-01-01")
assert no3["date"].max() <= pd.Timestamp("2024-12-31")
assert no3["filled_degree"].between(0, 1).all()
```

#### Gotchas

- **No date parameters.** Sending `?startDate=...` is silently ignored. Filter after download.
- **ISO strings.** `neste_Publiseringsdato` includes `T00:00:00` and must be parsed before use.
- **It is weekly.** Do not resample to daily without deciding how (interpolate or forward-fill).
- **One bad timeout kills the notebook.** `timeout=120` + `raise_for_status()`.
- **Cache it.** Download once per session; the existing app uses `@st.cache_data`.

---

### 5.2 open-meteo ERA5 (the big one)

#### 5.2.1 Read the docs the smart way

Go to **https://open-meteo.com/en/docs** and choose the **Historical Weather API**. On that page:

1. Tick **Hourly** variables: `temperature_2m`, `precipitation`, plus extras such as `relative_humidity_2m`, `wind_speed_10m`, `shortwave_radiation`, `snow_depth`.
2. Set a location and date range.
3. Pick **Model: ERA5** (this is the reanalysis model the task asks for).
4. Scroll to the bottom: the page generates a ready Python `requests` call.

The generated code is the starting point; the guide below turns it into the region-download function you need.

#### 5.2.2 Endpoint and parameters

```
GET https://archive-api.open-meteo.com/v1/archive
```

| Parameter | Value for this task |
|---|---|
| `latitude` | one value **or comma-separated list** |
| `longitude` | one value **or comma-separated list** |
| `start_date` | `YYYY-MM-DD` |
| `end_date` | `YYYY-MM-DD` |
| `hourly` | `temperature_2m,precipitation,...` |
| `models` | `era5` |
| `timezone` | `UTC` (recommended: makes joining with other data easy) |

#### 5.2.3 What the response looks like

**One location → one JSON object:**

```json
{
  "latitude": 59.9,
  "longitude": 10.75,
  "hourly_units": {"time": "iso8601", "temperature_2m": "°C", "precipitation": "mm"},
  "hourly": {
    "time": ["2024-01-01T00:00", "2024-01-01T01:00", "..."],
    "temperature_2m": [-3.0, -3.1, "..."],
    "precipitation": [0.0, 0.1, "..."]
  }
}
```

**Many locations → a JSON list, same order as the request:**

```json
[ {location 1}, {location 2}, ... ]
```

Two details that bite people:

- **Coordinates are snapped to the model grid.** Asking for `59.91` may return `60.0`. Carry your own `point_id`; do not identify points by the returned lat/lon.
- **The list order matches the request order**, so `zip(points, response)` is safe.

#### 5.2.4 Step 1 — one point, one year

```python
import requests
import pandas as pd

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 59.91,
    "longitude": 10.75,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "hourly": "temperature_2m,precipitation",
    "models": "era5",
    "timezone": "UTC",
}

response = requests.get(ARCHIVE_URL, params=params, timeout=90)
response.raise_for_status()
payload = response.json()["hourly"]

df = pd.DataFrame(payload)
df["time"] = pd.to_datetime(df["time"])
print(df.shape)      # (8784, 3) — 2024 is a leap year
print(df.head())
```

#### 5.2.5 Step 2 — many points in batches

Batching matters: 1 000 points in one URL is too long, and the response is huge.

```python
def fetch_openmeteo(points, start, end,
                    variables=("temperature_2m", "precipitation"),
                    batch_size=50):
    """Download ERA5 hourly data for a list of {'id','lat','lon'} points."""
    frames = []

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        params = {
            "latitude": ",".join(f"{p['lat']:.4f}" for p in batch),
            "longitude": ",".join(f"{p['lon']:.4f}" for p in batch),
            "start_date": start,
            "end_date": end,
            "hourly": ",".join(variables),
            "models": "era5",
            "timezone": "UTC",
        }

        response = requests.get(ARCHIVE_URL, params=params, timeout=180)
        response.raise_for_status()
        payload = response.json()

        # one location -> dict; many -> list
        if isinstance(payload, dict):
            payload = [payload]

        for point, location in zip(batch, payload):
            frame = pd.DataFrame(location["hourly"])
            frame["time"] = pd.to_datetime(frame["time"])
            frame["point_id"] = point["id"]
            frame["lat"] = point["lat"]
            frame["lon"] = point["lon"]
            frames.append(frame)

    return pd.concat(frames, ignore_index=True)
```

#### 5.2.6 Step 3 — sample 1 000 points inside a polygon

Download the polygons first (§5.3), then:

```python
import numpy as np
from shapely.geometry import Point

def sample_points_in_polygon(polygon, n=1000, seed=42):
    """Rejection-sample n points inside a shapely polygon."""
    rng = np.random.default_rng(seed)
    minx, miny, maxx, maxy = polygon.bounds
    points = []

    while len(points) < n:
        xs = rng.uniform(minx, maxx, size=n)
        ys = rng.uniform(miny, maxy, size=n)
        for x, y in zip(xs, ys):
            candidate = Point(x, y)
            if polygon.contains(candidate):
                points.append({"lat": y, "lon": x})
                if len(points) == n:
                    break

    for i, point in enumerate(points):
        point["id"] = i
    return points
```

> The bounding box of Norway is much larger than the land area, so this is slower than it looks. If it feels slow, sample 3–4× `n` candidates at once and filter with `polygon.contains` in a loop — same result, fewer Python-level iterations.

#### 5.2.7 Step 4 — aggregate to one series per region

A region's weather is the **mean over its 1 000 points at each timestamp**:

```python
hourly = fetch_openmeteo(points, "2024-01-01", "2024-12-31")

region_hourly = (
    hourly.groupby("time")[["temperature_2m", "precipitation"]]
    .mean()
    .sort_index()
)

print(region_hourly.shape)   # (8784, 2)
```

Then make daily series for the plots and analyses:

```python
daily = pd.DataFrame({
    "temperature": region_hourly["temperature_2m"].resample("D").mean(),
    "precipitation": region_hourly["precipitation"].resample("D").sum(),
})
```

- **Temperature**: average (`.mean()`)
- **Precipitation**: sum per day (`.sum()`), because mm is an accumulation

#### 5.2.8 Complete region download function

```python
def download_weather_for_region(region_id, start, end, *,
                                variables=("temperature_2m", "precipitation",
                                           "relative_humidity_2m", "wind_speed_10m"),
                                batch_size=50):
    """Region id + interval -> hourly region-mean weather DataFrame."""
    points = load_region_points(region_id)          # from data/regions/*.csv
    hourly = fetch_openmeteo(points, start, end,
                             variables=variables,
                             batch_size=batch_size)
    region_hourly = hourly.groupby("time")[list(variables)].mean()
    region_hourly["region_id"] = region_id
    return region_hourly.sort_index()
```

Where `load_region_points` is tiny:

```python
from pathlib import Path

def load_region_points(region_id):
    """Read the saved 1 000 sampled coordinates for a region."""
    path = Path("data/regions") / f"points_{region_id}.csv"
    return pd.read_csv(path).to_dict("records")
```

#### 5.2.9 Limits and gotchas

| Gotcha | What to do |
|---|---|
| **Huge responses** | 1 000 points × 1 year × 2 variables ≈ **274 MB** JSON; 6 variables ≈ **800 MB**. Aggregate immediately, never keep raw per-point data. |
| **URL length** | Batch 50–100 locations per request. |
| **Rate limits** | Free API has daily/hourly limits. Add a short `time.sleep(0.2)` between batches and retry on HTTP 429. |
| **Timeouts** | Use `timeout=180` for big batches. |
| **Coordinate snapping** | Keep your own `point_id`; the returned lat/lon is the grid cell. |
| **Leap year** | 2024 has 8 784 hours, not 8 760. Assert the row count in tests. |
| **Missing values** | Ocean/edge points can return `null`. Prefer land points from the polygon and drop/forward-fill knowingly. |
| **Caching** | Save the aggregated result to parquet (`data/regions/weather_<region>_<year>.parquet`) and upload to MongoDB. Re-running the notebook should not re-download 274 MB. |

#### 5.2.10 Verify

```python
assert len(region_hourly) == 8784
assert region_hourly["temperature_2m"].notna().all()
assert region_hourly["precipitation"].min() >= 0
assert region_hourly["precipitation"].sum() > 0
```

---

### 5.3 NVE geodata / shapefiles

#### 5.3.1 What you need

| Shapefile / layer | Used for | Codes |
|---|---|---|
| Electricity price areas | `EL` 1–5 | `NO1`–`NO5` |
| NVE administrative regions | `VASS` 1–3 (precipitation areas) | `RS`, `RØ`, `RV`, `RM`, `RN` |

**Why the task says "East is split into RS+RØ, and North is split into RM+RN":**

| Magasinstatistikk area | NVE region(s) |
|---|---|
| `VASS 1` — South-East (Austlandet, Agder, parts of Rogaland) | **RS + RØ** |
| `VASS 2` — West (rest of Rogaland, most of Vestland) | **RV** |
| `VASS 3` — Central & North (Møre, Trøndelag, Nord-Norge) | **RM + RN** |

This mapping is confirmed against NVE's own region layer and their description of the three watercourse areas.

#### 5.3.2 Where to download

**Option A — atlas.nve.no (as the task says):**

1. Open <https://atlas.nve.no>.
2. Open the layer list → **Administrasjon / NVE regioner** (and the electricity price areas if shown there).
3. Use the download/export tool and choose **Shapefile** or **GeoJSON**, coordinate system **EPSG:4326**.

**Option B — direct GeoJSON from NVE's map service (tested working):**

```python
import requests

REGION_URL = (
    "https://kart.nve.no/enterprise/rest/services/Mapservices/"
    "Administrasjon2/MapServer/0/query"
)

params = {
    "where": "1=1",
    "outFields": "REGION,REGIONNAVN",
    "returnGeometry": "true",
    "outSR": "4326",
    "f": "geojson",
}

response = requests.get(REGION_URL, params=params, timeout=60)
response.raise_for_status()

with open("data/regions/NVE_Region.geojson", "w", encoding="utf-8") as file:
    file.write(response.text)
```

This returns the five polygons **RV, RM, RN, RØ, RS** with properties `REGION` and `REGIONNAVN`. (Verified live.)

**Electricity areas:** NVE's accessible REST services do not expose a dedicated NO1–NO5 polygon layer. Find it in atlas.nve.no; if it is not there, source a published NO1–NO5 GeoJSON (Statnett / ENTSO-E) and document the URL in the notebook. **This is the only data source still uncertain — solve it early.**

#### 5.3.3 Read the polygons with geopandas

```python
import geopandas as gpd

regions = gpd.read_file("data/regions/NVE_Region.geojson").to_crs(4326)
print(regions[["REGION", "REGIONNAVN"]])
print(regions.crs)
```

#### 5.3.4 Build the region → polygon map

```python
REGION_MAP = {
    "NO1": ["NO1"],
    "NO2": ["NO2"],
    "NO3": ["NO3"],
    "NO4": ["NO4"],
    "NO5": ["NO5"],
    "VASS1": ["RS", "RØ"],
    "VASS2": ["RV"],
    "VASS3": ["RM", "RN"],
}

def region_polygon(region_id, regions):
    """Union of one or more polygons for a region id."""
    if region_id.startswith("VASS"):
        codes = REGION_MAP[region_id]
        subset = regions[regions["REGION"].isin(codes)]
    else:
        subset = regions[regions["REGION"] == region_id]
    return subset.geometry.union_all()
```

> `union_all()` is the current geopandas/GeoSeries API (geopandas ≥ 1.0). On older versions use `subset.geometry.unary_union`.
>
> The EL file may use a different attribute name than `REGION` (e.g. `NO`, `område`, `name`). Open the file once, print `regions.columns`, and change the column name in `region_polygon` accordingly.

#### 5.3.5 Save the sampled points

```python
import pandas as pd
from pathlib import Path

out_dir = Path("data/regions")
out_dir.mkdir(parents=True, exist_ok=True)

for region_id in ["NO1", "NO2", "NO3", "NO4", "NO5",
                  "VASS1", "VASS2", "VASS3"]:
    polygon = region_polygon(region_id, regions)
    points = sample_points_in_polygon(polygon, n=1000, seed=42)
    pd.DataFrame(points).to_csv(out_dir / f"points_{region_id}.csv", index=False)
    print(region_id, len(points))
```

Commit `data/regions/points_*.csv` (small, ~50 KB each) so the download is reproducible. You can ignore the `.geojson` if it is large, or commit it too — it is a few MB.

---

### 5.4 MongoDB (upload + read)

The task requires the app to read data **uploaded to MongoDB** and data **directly from the APIs**. Use MongoDB for the weather (heavy, cached) and keep Magasinstatistikk direct (small, fast).

#### 5.4.1 Connect

```python
import tomllib
from pymongo import MongoClient

with open(".streamlit/secrets.toml", "rb") as file:
    secrets = tomllib.load(file)

uri = (
    f"mongodb+srv://{secrets['usernameMongoDB']}:{secrets['passwordMongoDB']}"
    "@ind320db.peyqaxm.mongodb.net/?appName=IND320DB"
)

client = MongoClient(uri, serverSelectionTimeoutMS=20_000)
```

#### 5.4.2 Recommended document model

One document per region per year, with parallel arrays (compact, fits the free tier):

```python
{
    "region_id": "VASS1",
    "area_type": "VASS",
    "area_nr": 1,
    "year": 2024,
    "time": [datetime, ...],              # 8784 entries
    "temperature_2m": [float, ...],
    "precipitation": [float, ...],
    "relative_humidity_2m": [float, ...],
    "wind_speed_10m": [float, ...],
    "n_points": 1000,
}
```

≈ 10 regions × 8 784 hours × 4 variables ≈ 350 000 numbers — only a few MB in total.

#### 5.4.3 Write (upsert = safe to re-run)

```python
from datetime import datetime, timezone

db = client["meteo"]
collection = db["regionYear"]
collection.create_index([("region_id", 1), ("year", 1)], unique=True)

document = {
    "region_id": "VASS1",
    "area_type": "VASS",
    "area_nr": 1,
    "year": 2024,
    "time": region_hourly.index.to_pydatetime().tolist(),
    "temperature_2m": region_hourly["temperature_2m"].tolist(),
    "precipitation": region_hourly["precipitation"].tolist(),
    "n_points": 1000,
    "created": datetime.now(timezone.utc),
}

collection.replace_one(
    {"region_id": "VASS1", "year": 2024},
    document,
    upsert=True,
)
```

#### 5.4.4 Read back and verify

```python
document = collection.find_one({"region_id": "VASS1", "year": 2024}, {"_id": 0})
weather = pd.DataFrame(document).set_index("time")
weather.index = pd.to_datetime(weather.index)

print(weather.shape)          # (8784, ...)
print(weather.head())
```

#### 5.4.5 Gotchas

- **Do not commit `secrets.toml`.** It is already ignored.
- **`_id` breaks pandas/plotly** — drop it in `find` projections or with `{"_id": 0}`.
- **Free tier is 512 MB.** Arrays are far smaller than 500k documents.
- **Upsert, not insert** — the notebook must be safe to run twice.
- **Timezone**: store UTC datetimes, parse with `pd.to_datetime` on read.
- **Create the index once**; `create_index` is idempotent.

---

## 6. Notebook — build guide

Create/refresh `notebooks/Oblig3.ipynb` with these sections. Put reusable logic in `utils/meteo.py` and `utils/analysis.py` and import it, so the notebook and app share the same code.

### 6.1 Section: Setup

```python
import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parent))   # so "utils" is importable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.dataLoaders import load_magazine_data_api
```

### 6.2 Section: Areas and sampled points

- Show the NVE region polygons and the VASS mapping table.
- Plot the polygons + sampled points on a map (matplotlib scatter is enough).
- Save/load `data/regions/points_*.csv`.

### 6.3 Section: Weather download

- Show the single-point example (§5.2.4) first — it makes the API obvious.
- Then the full region function and **NO3 2024**.
- Plot hourly/daily average temperature and precipitation (sanity check).
- Save the aggregated frame to parquet.

### 6.4 Section: Outliers — precipitation (DCT + SPC)

**Idea:** the seasonal cycle is low-frequency. Remove it with a DCT high-pass; the residual is the **seasonally adjusted variation (SATV)**. Robust bounds on the SATV decide what is an outlier. Do **not** plot the SATV — only use it to colour points and draw curves.

```python
from scipy.fft import dct, idct

def dct_spc_outliers(series, cutoff_days=30, n_sigma=3.0):
    """
    series: daily pd.Series (e.g. average precipitation)
    cutoff_days: periods longer than this are removed (seasonal cycle)
    n_sigma: robust SPC width in robust standard deviations
    """
    x = series.to_numpy(dtype=float)
    n = len(x)

    # 1) high-pass: keep only fast variations
    coefficients = dct(x, norm="ortho")
    cutoff_index = max(1, int(n / cutoff_days))
    coefficients[:cutoff_index] = 0.0
    satv = idct(coefficients, norm="ortho")

    # 2) robust statistics from the whole year
    centre = np.median(satv)
    sigma = 1.4826 * np.median(np.abs(satv - centre))   # MAD -> sigma
    lower_satv = centre - n_sigma * sigma
    upper_satv = centre + n_sigma * sigma

    # 3) map bounds back to the original scale
    baseline = x - satv
    lower = baseline + lower_satv
    upper = baseline + upper_satv

    outliers = (x < lower) | (x > upper)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(series.index, x, color="steelblue", label="Precipitation")
    ax.plot(series.index, lower, "k--", linewidth=1, label="SPC lower")
    ax.plot(series.index, upper, "k--", linewidth=1, label="SPC upper")
    ax.scatter(series.index[outliers], x[outliers], color="crimson",
               zorder=3, label="Outlier")
    ax.set_ylabel("Precipitation (mm/day)")
    ax.legend()

    summary = pd.DataFrame({
        "date": series.index[outliers],
        "value": x[outliers],
    })
    return fig, summary
```

**Parameters and defaults** (must be arguments, per the task):

| Parameter | Default | Meaning |
|---|---|---|
| `cutoff_days` | `30` | periods longer than 30 days are removed |
| `n_sigma` | `3.0` | SPC width in robust σ |

**Test it:**

```python
synthetic = pd.Series(
    np.sin(np.linspace(0, 2 * np.pi, 365)) + np.random.normal(0, 0.1, 365),
    index=pd.date_range("2024-01-01", periods=365),
)
synthetic.iloc[100] += 10     # known outlier
fig, summary = dct_spc_outliers(synthetic)
assert pd.Timestamp("2024-04-10") in summary["date"].values
```

### 6.5 Section: Anomalies — temperature (LOF)

```python
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

def lof_anomalies(series, contamination=0.01, n_neighbors=20):
    """Flag anomalies in a 1-D series with Local Outlier Factor."""
    values = series.to_numpy(dtype=float).reshape(-1, 1)
    values = StandardScaler().fit_transform(values)

    lof = LocalOutlierFactor(n_neighbors=n_neighbors,
                             contamination=contamination)
    labels = lof.fit_predict(values)          # -1 = anomaly
    anomalies = labels == -1

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(series.index, series, color="darkorange", label="Temperature")
    ax.scatter(series.index[anomalies], series[anomalies],
               color="crimson", zorder=3, label="Anomaly")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()

    summary = pd.DataFrame({
        "date": series.index[anomalies],
        "value": series[anomalies],
    })
    return fig, summary
```

| Parameter | Default |
|---|---|
| `contamination` | `0.01` (1 %, as required) |
| `n_neighbors` | `20` |

**Test:** build a cluster around 0 and put two obvious spikes at +20; both must be flagged. Then check that roughly 1 % of the real NO3 year is flagged.

### 6.6 Section: STL

```python
from statsmodels.tsa.seasonal import STL

def stl_decomposition(series, period=52, seasonal=13, trend=53, robust=True):
    """STL decomposition of a weekly series (e.g. filled_degree).

    statsmodels requires: seasonal odd and >= 3, trend odd and > period.
    """
    result = STL(series, period=period, seasonal=seasonal,
                 trend=trend, robust=robust).fit()

    fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
    axes[0].plot(series);                 axes[0].set_ylabel("Observed")
    axes[1].plot(result.trend);           axes[1].set_ylabel("Trend")
    axes[2].plot(result.seasonal);        axes[2].set_ylabel("Seasonal")
    axes[3].plot(result.resid);           axes[3].set_ylabel("Residual")
    fig.tight_layout()
    return fig, result
```

| Parameter | Default | Note |
|---|---|---|
| `period` | `52` | weekly data |
| `seasonal` | `13` | must be **odd** and ≥ 3 |
| `trend` | `53` | must be **odd and greater than `period`** — `trend=25` with `period=52` raises an error |
| `robust` | `True` | down-weights outliers |

**Data:** `filled_degree` for one area (e.g. `VASS 1` or `EL 3` from `load_magasinstatistikk`). There are 30+ years, so STL has plenty of periods.

**Test:** `(trend + seasonal + resid) ≈ observed`, no NaNs.

### 6.7 Section: Spectrogram

```python
from scipy import signal

def spectrogram_plot(series, window=52, overlap=0.5):
    """Spectrogram of a weekly series. window = weeks, overlap = fraction."""
    values = series.to_numpy(dtype=float)
    nperseg = min(window, len(values))
    noverlap = int(nperseg * overlap)

    frequencies, times, power = signal.spectrogram(
        values, fs=1.0, nperseg=nperseg, noverlap=noverlap,
        detrend="linear", scaling="density",
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    mesh = ax.pcolormesh(times, frequencies, 10 * np.log10(power + 1e-12),
                         shading="auto")
    ax.set_ylabel("Frequency (cycles/week)")
    ax.set_xlabel("Time (weeks)")
    fig.colorbar(mesh, ax=ax, label="Power (dB)")
    return fig, frequencies, times, power
```

| Parameter | Default |
|---|---|
| `window` | `52` weeks |
| `overlap` | `0.5` (50 % = 26 weeks) |

**Test:** a synthetic sine with a 26-week period must produce a peak at `1/26 ≈ 0.038` cycles/week. Also test the default on the real `filled_degree` series.

### 6.8 Section: Save to MongoDB

Upload the aggregated NO3 (and any other regions) using §5.4. Print the read-back shape as proof.

### 6.9 Section: AI usage, log, links

- **AI usage:** 4–8 sentences. (Oblig 1/2 already have a style you can follow.)
- **Log (300–500 words):** what you built in the notebook, what you built in Streamlit, problems, decisions, what you would do differently.
- **Links:** GitHub repo + Streamlit app + screencast.
- **Export:** run every cell, then `File → Save and Export Notebook As → PDF` (or `jupyter nbconvert --to pdf`). Commit the `.ipynb`.

---

## 7. Streamlit — build guide

### 7.1 Page map (recommended order)

| # | Page | Content |
|---|---|---|
| 1 | Home | existing |
| 2 | Reservoir tables | existing |
| 3 | Reservoir plots | existing |
| 4 | **Meteorological data** | area selector, status, download button, preview |
| 5 | **Reservoir analysis** | tabs: STL \| Spectrogram |
| 6 | **Weather analysis** | tabs: Outliers/SPC \| Anomalies/LOF |
| 7 | Transmission plots | existing |
| 8 | Settings | admin only |

### 7.2 Reuse the existing area selector

`utils/areaSelect.py` already gives you `(areaType, areaNr)` with `EL`/`NO`/`VASS`. Use a **local key per page** so widgets do not collide:

```python
from utils.areaSelect import areaSelector, filterArea
areaType, areaNr = areaSelector(fullReservoirs, "meteo")
```

Map the selection to a weather region:

```python
def area_to_region(area_type, area_nr):
    if area_type == "EL":
        return f"NO{area_nr}"
    if area_type == "VASS":
        return f"VASS{area_nr}"
    return "NO"          # whole country (download/sample all regions if needed)
```

### 7.3 Meteorological data page (`pages/meteorologicalData.py`)

Logic:

1. Load Magasinstatistikk (`load_magazine_data_api`, cached).
2. Area selector → `region_id`.
3. Look up `meteo.regionYear` for `{region_id, year}`.
4. If **missing**: show an info box + a **Download** button.
5. If **present**: show the temperature and precipitation plots + a small status table.
6. Download button: `st.spinner(...)` → `download_weather_for_region(...)` → Mongo upsert → `st.rerun()`.

Skeleton:

```python
import streamlit as st
from utils.dataLoaders import load_magazine_data_api
from utils.areaSelect import areaSelector
from utils.meteo import area_to_region, load_weather, download_and_store

st.set_page_config(page_title="Meteorological data", page_icon="🌦️", layout="wide")

magasin = load_magazine_data_api()
area_type, area_nr = areaSelector(magasin, "meteo")
region_id = area_to_region(area_type, area_nr)

st.subheader(f"Weather for {region_id}")
weather = load_weather(region_id, 2024)

if weather is None or weather.empty:
    st.info("No weather data in MongoDB for this region/year yet.")
    if st.button("Download from open-meteo (ERA5)"):
        with st.spinner("Sampling 1 000 points and downloading 2024..."):
            download_and_store(region_id, 2024)
        st.rerun()
else:
    st.line_chart(weather[["temperature_2m"]])
    st.bar_chart(weather[["precipitation"]])
    st.caption(f"{len(weather):,} hourly rows from MongoDB")
```

The two helpers used by the page (`utils/meteo.py`):

```python
def load_weather(region_id, year):
    """Read one region-year document from MongoDB and return a DataFrame."""
    document = collection.find_one(
        {"region_id": region_id, "year": year}, {"_id": 0}
    )
    if not document:
        return None

    frame = pd.DataFrame(
        {key: value for key, value in document.items() if isinstance(value, list)}
    )
    frame["time"] = pd.to_datetime(frame["time"])
    return frame.set_index("time")


def download_and_store(region_id, year):
    """Download one region-year from open-meteo and upsert it into MongoDB."""
    weather = download_weather_for_region(
        region_id, f"{year}-01-01", f"{year}-12-31"
    )
    collection.replace_one(
        {"region_id": region_id, "year": year},
        {
            "region_id": region_id,
            "year": year,
            "time": pd.to_datetime(weather.index).to_pydatetime().tolist(),
            **{
                column: weather[column].tolist()
                for column in weather.columns
                if column != "region_id"
            },
            "n_points": 1000,
        },
        upsert=True,
    )
    return weather
```

### 7.4 Reservoir analysis page (`pages/reservoirAnalysis.py`)

```python
tab_stl, tab_spec = st.tabs(["STL", "Spectrogram"])

with tab_stl:
    col1, col2, col3 = st.columns(3)
    seasonal = col1.slider("Seasonal smoother", 3, 51, 13, step=2)
    # trend must be odd and > period (52) -> slider starts at 53
    trend = col2.slider("Trend smoother", 53, 201, 53, step=2)
    robust = col3.checkbox("Robust", value=True)
    # plot via utils.analysis.stl_decomposition(...)

with tab_spec:
    window = st.slider("Window length (weeks)", 8, 104, 52)
    overlap = st.slider("Overlap", 0.0, 0.9, 0.5, step=0.1)
    # plot via utils.analysis.spectrogram_plot(...)
```

Use the shared area selector above the tabs, then filter `filled_degree` for that area.

### 7.5 Weather analysis page (`pages/weatherAnalysis.py`)

```python
tab_spc, tab_lof = st.tabs(["Outliers / SPC", "Anomalies / LOF"])

with tab_spc:
    cutoff = st.slider("DCT cutoff (days)", 7, 120, 30)
    n_sigma = st.slider("SPC width (sigma)", 1.0, 5.0, 3.0, step=0.5)
    # plot precipitation + bounds + red outliers, summary metrics

with tab_lof:
    contamination = st.slider("Expected outlier share", 0.001, 0.05, 0.01, step=0.001)
    # plot temperature + red anomalies, summary metrics
```

Show the summaries as `st.metric` (count, %, strongest outlier) or `st.dataframe`.

### 7.6 Register and reorder pages

In `streamlit_app.py`:

```python
pageMeteo = st.Page("pages/meteorologicalData.py", title="Meteorological data", icon="🌦️")
pageReservoirAnalysis = st.Page("pages/reservoirAnalysis.py", title="Reservoir analysis", icon="🔬")
pageWeatherAnalysis = st.Page("pages/weatherAnalysis.py", title="Weather analysis", icon="🌡️")

pages = [pageHome, pageTables, pagePlots, pageMeteo,
         pageReservoirAnalysis, pageWeatherAnalysis,
         pageTransmission]
if st.session_state.userRole == UserRoles.ADMIN:
    pages.append(pageSettings)
```

### 7.7 Global vs local selector

Keep the selector **local to each page** (via the `key` argument). Reasons:

- the tables/plots pages may show one area while the analysis page compares another;
- local keys avoid widgets overwriting each other;
- no global state to reset.

Document this decision in the notebook log.

---

## 8. Run order (copy-paste)

Do it in this order. Each step produces something you can verify.

```bash
# 0) branch + deps
cd Code/IND320/IND320LjosNorth
git switch -c oblig3
uv add scipy geopandas pyarrow
uv sync

# 1) sanity check the old app still works
uv run streamlit run streamlit_app.py

# 2) notebook: areas -> points -> open-meteo -> parquet
uv run jupyter lab notebooks/Oblig3.ipynb

# 3) analyses in the notebook (DCT/SPC, LOF, STL, spectrogram), then tests
# 4) upload region means to MongoDB, verify read-back
# 5) build utils/meteo.py + utils/analysis.py from the notebook code
# 6) build the three pages, register in streamlit_app.py
# 7) run the app and test every tab and selector
# 8) notebook log + AI section + run-all + PDF export
# 9) screencast (5 min) + link in notebook
# 10) commit and push the branch
```

---

## 9. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: geopandas` | `uv add geopandas && uv sync` |
| `SSLError` / timeout on NVE | Retry; the endpoint is sometimes slow. Increase `timeout`. |
| open-meteo returns `null` values | Ocean/edge points. Sample only land polygons; drop or fill deliberately. |
| open-meteo HTTP 429 | Rate limit. Lower batch rate, `time.sleep(0.5)`, retry. |
| `MemoryError` during download | You kept per-point raw frames. Aggregate each batch before appending. |
| Mongo `ServerSelectionTimeoutError` | Wrong credentials / IP not allowed. Check `.streamlit/secrets.toml` and Atlas network access. |
| `st.session_state has no attribute "userRole"` | A page was run directly. Always run `streamlit_app.py`. |
| Streamlit shows old data | `@st.cache_data` — clear cache or change the function arguments. |
| STL error about period | `period=52` needs ≥ 104 weekly observations. The full history has enough; 2024 alone does not. |
| `trend must be ... > period` | statsmodels requires `trend` **odd and greater than `period`**. Use `trend=53` for `period=52`. |
| DCT flags a small cluster instead of one spike | A sharp spike makes neighbouring DCT coefficients ring. Expect a few nearby outliers; that is normal for a global transform. |
| Spectrogram is empty | `nperseg` longer than the series. Cap `nperseg` at `len(series)`. |
| DCT bounds look wrong | Remember to add the seasonal baseline back before plotting on mm/day. |

---

## 10. Final hand-in checklist

### Repo
- [ ] Oblig 3 code committed on `Dev`/`oblig3`
- [ ] `notebooks/Oblig3.ipynb` committed with outputs
- [ ] No secrets committed
- [ ] README + CHANGELOG updated

### Notebook
- [ ] 1 000 points per region documented
- [ ] NO3 2024 downloaded
- [ ] Precipitation + SPC plot with outlier summary
- [ ] Temperature + LOF plot with anomaly summary
- [ ] STL decomposition plot
- [ ] Spectrogram
- [ ] Each analysis function has a test cell
- [ ] 300–500 word log
- [ ] AI usage section
- [ ] Links to repo + app
- [ ] PDF exported after run-all

### App
- [ ] Meteorological data page (selector + download + status)
- [ ] STL / Spectrogram tabs
- [ ] SPC / LOF tabs
- [ ] Pages reordered
- [ ] Existing pages still work
- [ ] Deployed and reachable online

### Screencast
- [ ] ~5 minutes
- [ ] Shows the app and explains the code
- [ ] Link/permissions verified

---

## 11. Time estimate

| Part | Time |
|---|---|
| Branch, deps, repo hygiene | 0.5 h |
| Shapefiles + mapping + 1 000-point sampling | 3–5 h |
| open-meteo download + aggregation + Mongo upload | 3–4 h |
| DCT/SPC + LOF | 3–4 h |
| STL + spectrogram | 2–3 h |
| Three Streamlit pages + page order | 3–4 h |
| Notebook narrative, log, AI, PDF | 2 h |
| Screencast | 1 h |
| Final QA | 1 h |
| **Total** | **≈ 19–25 h** |

---

*End of report.*
