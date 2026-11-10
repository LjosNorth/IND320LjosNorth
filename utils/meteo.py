"""
This is some slop to get the API stuff done, it should ***Not Be Called*** anymore

Weather data pipeline for Oblig 3.

Downloads ERA5 daily weather for a shared 0.5 degree grid, aggregates the
cells to the Magasinstatistikk regions, saves one folder per region, and
uploads the result to MongoDB.

The shared-grid approach keeps the API cost manageable::

    426 cells * 3 variables * 366 days / 140 ~= 3 341 API calls

instead of downloading 8 regions * 1 000 points (~62 700 calls).

Output layout::

    data/regions/samples/weather/
        cells_0p5.csv
        cell_daily_0p5.parquet
        batches_0p5/
            batch_0000_0050.parquet
            ...
        NO1/
            daily.parquet
            weights.csv
        ...
        VASS3/
            daily.parquet
            weights.csv
        NO/
            daily.parquet          # area-weighted average of NO1-NO5

The MongoDB collection is ``entsoE.weather``. One document per region and
day:

    {
        "region_id": "NO3",
        "year": 2024,
        "time": datetime,
        "temperature_2m": float,
        "precipitation": float,
        "wind_speed_10m": float
    }

Run the module from the repository root::

    python -m utils.meteo download
    python -m utils.meteo upload

or import the functions::

    from utils.meteo import download_all_regions, upload_weather_to_mongo

    download_all_regions()
    upload_weather_to_mongo()
"""

from __future__ import annotations

import argparse
import time
import tomllib
from pathlib import Path

import pandas as pd
import requests
from pymongo import MongoClient

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
REGIONS_DIR = ROOT / "data" / "regions"
SAMPLES_DIR = REGIONS_DIR / "samples"
WEATHER_DIR = SAMPLES_DIR / "weather"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

REGIONS = ["NO1", "NO2", "NO3", "NO4", "NO5", "VASS1", "VASS2", "VASS3"]
NORWAY_REGIONS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
ALL_REGIONS = REGIONS + ["NO"]

DAILY_VARIABLES = (
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_mean",
)

APP_COLUMNS = {
    "temperature_2m_mean": "temperature_2m",
    "precipitation_sum": "precipitation",
    "wind_speed_10m_mean": "wind_speed_10m",
}

DEFAULT_CELL_SIZE = 0.5
DEFAULT_START = "2024-01-01"
DEFAULT_END = "2024-12-31"
DEFAULT_COLLECTION = "weather"

__all__ = [
    "build_cells",
    "fetch_cell_weather",
    "build_region_daily",
    "build_norway_daily",
    "download_all_regions",
    "upload_weather_to_mongo",
    "load_weather",
]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _tag(cell_size: float) -> str:
    """Return a filename-safe tag for a cell size, e.g. 0.5 -> '0p5'."""
    return f"{cell_size:g}".replace(".", "p")


def _sample_file(region: str) -> Path:
    """Return the sample CSV for a normalised region id.

    The electricity-area files currently use a space
    (``samples_NO 1.csv``), while the VASS files do not
    (``samples_VASS1.csv``). Both spellings are accepted.
    """
    candidates = [SAMPLES_DIR / f"samples_{region}.csv"]
    if region.startswith("NO") and region != "NO":
        candidates.append(SAMPLES_DIR / f"samples_NO {region[-1]}.csv")

    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _region_folder(region: str, weather_dir: Path) -> Path:
    """Return (and create) the output folder for one region."""
    folder = weather_dir / region
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _mongo_uri() -> str:
    """Build the MongoDB URI from ``.streamlit/secrets.toml``."""
    secrets_path = ROOT / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        raise FileNotFoundError(
            "Add usernameMongoDB and passwordMongoDB to .streamlit/secrets.toml"
        )
    secrets = tomllib.loads(secrets_path.read_text())
    return (
        f"mongodb+srv://{secrets['usernameMongoDB']}:{secrets['passwordMongoDB']}"
        "@ind320db.peyqaxm.mongodb.net/?appName=IND320DB"
    )


# ---------------------------------------------------------------------------
# 1. Shared ERA5 grid
# ---------------------------------------------------------------------------


def build_cells(
    cell_size: float = DEFAULT_CELL_SIZE,
    *,
    weather_dir: Path = WEATHER_DIR,
    force: bool = False,
) -> pd.DataFrame:
    """Build the unique ERA5 grid cells from all regional samples.

    Parameters
    ----------
    cell_size : float, optional
        Grid size in degrees. Default is 0.5.
    weather_dir : pathlib.Path, optional
        Output directory. Default is ``data/regions/samples/weather``.
    force : bool, optional
        Rebuild the file even if it already exists. Default is False.

    Returns
    -------
    pandas.DataFrame
        Columns ``cell_id``, ``lat_cell`` and ``lon_cell``.
    """
    weather_dir.mkdir(parents=True, exist_ok=True)
    path = weather_dir / f"cells_{_tag(cell_size)}.csv"

    if path.exists() and not force:
        return pd.read_csv(path)

    frames = []
    for region in REGIONS:
        sample = _sample_file(region)
        if not sample.exists():
            raise FileNotFoundError(f"Missing sample file for {region}: {sample}")
        points = pd.read_csv(sample)
        points["lat_cell"] = (points["lat"] / cell_size).round() * cell_size
        points["lon_cell"] = (points["lon"] / cell_size).round() * cell_size
        frames.append(points[["lat_cell", "lon_cell"]])

    cells = (
        pd.concat(frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
    )
    cells["cell_id"] = range(len(cells))
    cells = cells[["cell_id", "lat_cell", "lon_cell"]]
    cells.to_csv(path, index=False)

    print(f"Built {len(cells)} unique {cell_size:g}° cells -> {path}")
    return cells


# ---------------------------------------------------------------------------
# 2. API download
# ---------------------------------------------------------------------------


def fetch_cell_weather(
    cells: pd.DataFrame,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    *,
    cell_size: float = DEFAULT_CELL_SIZE,
    batch_size: int = 50,
    weather_dir: Path = WEATHER_DIR,
    force: bool = False,
) -> pd.DataFrame:
    """Download daily ERA5 weather for a set of grid cells.

    Parameters
    ----------
    cells : pandas.DataFrame
        Output of :func:`build_cells`.
    start, end : str
        Inclusive date range.
    cell_size : float, optional
        Grid size used for the cache filename. Default is 0.5.
    batch_size : int, optional
        Cells per HTTP request. Default is 50.
    weather_dir : pathlib.Path, optional
        Cache directory.
    force : bool, optional
        Ignore cached batches. Default is False.

    Returns
    -------
    pandas.DataFrame
        Daily weather for every cell, with columns ``cell_id``,
        ``lat_cell``, ``lon_cell``, ``time`` and the daily variables.
    """
    if cells.empty:
        return pd.DataFrame()

    weather_dir.mkdir(parents=True, exist_ok=True)
    batch_dir = weather_dir / f"batches_{_tag(cell_size)}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    n_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    cost_per_cell = max(1.0, len(DAILY_VARIABLES) * n_days / 140.0)

    frames = []

    for batch_start in range(0, len(cells), batch_size):
        batch = cells.iloc[batch_start : batch_start + batch_size]
        batch_end = batch_start + len(batch)

        batch_file = batch_dir / f"batch_{batch_start:04d}_{batch_end:04d}.parquet"
        if batch_file.exists() and not force:
            frames.append(pd.read_parquet(batch_file))
            continue

        params = {
            "latitude": ",".join(f"{x:.4f}" for x in batch["lat_cell"]),
            "longitude": ",".join(f"{x:.4f}" for x in batch["lon_cell"]),
            "start_date": start,
            "end_date": end,
            "daily": ",".join(DAILY_VARIABLES),
            "models": "era5",
            "timezone": "UTC",
        }

        while True:
            response = requests.get(ARCHIVE_URL, params=params, timeout=180)

            if response.status_code == 429:
                retry = int(response.headers.get("Retry-After", 60))
                print(f"Rate limited. Sleeping {retry}s...")
                time.sleep(retry)
                continue

            response.raise_for_status()
            break

        payload = response.json()
        if isinstance(payload, dict):
            payload = [payload]

        if len(payload) != len(batch):
            raise RuntimeError(
                f"API returned {len(payload)} locations for {len(batch)} cells"
            )

        batch_frames = []
        for cell, location in zip(batch.itertuples(), payload):
            frame = pd.DataFrame(location["daily"])
            frame["time"] = pd.to_datetime(frame["time"])
            frame["cell_id"] = cell.cell_id
            frame["lat_cell"] = cell.lat_cell
            frame["lon_cell"] = cell.lon_cell
            batch_frames.append(frame)

        batch_df = pd.concat(batch_frames, ignore_index=True)
        batch_df.to_parquet(batch_file, index=False)
        frames.append(batch_df)

        print(f"Downloaded cells {batch_start}-{batch_end - 1} ({len(batch)} cells)")

        # Stay inside the 600/minute limit.
        remaining = float(response.headers.get("X-RateLimit-Remaining", 600))
        reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        next_cost = len(batch) * cost_per_cell

        if remaining < next_cost:
            sleep_for = max(0, reset - time.time()) + 1
            print(f"Minute limit nearly empty - sleeping {sleep_for:.0f}s...")
            time.sleep(sleep_for)

    cell_daily = pd.concat(frames, ignore_index=True)
    cell_daily = cell_daily.sort_values(["time", "cell_id"]).reset_index(drop=True)

    out_path = weather_dir / f"cell_daily_{_tag(cell_size)}.parquet"
    cell_daily.to_parquet(out_path, index=False)
    print(f"Saved cell-level daily weather -> {out_path}")

    return cell_daily


# ---------------------------------------------------------------------------
# 3. Aggregate cells to regions
# ---------------------------------------------------------------------------


def _region_weights(
    region: str,
    cell_size: float,
    weather_dir: Path,
) -> pd.DataFrame:
    """Return the cell weights for one region from its 1 000 sample points."""
    sample = _sample_file(region)
    if not sample.exists():
        raise FileNotFoundError(f"Missing sample file for {region}: {sample}")

    points = pd.read_csv(sample)
    points["lat_cell"] = (points["lat"] / cell_size).round() * cell_size
    points["lon_cell"] = (points["lon"] / cell_size).round() * cell_size

    weights = points.groupby(["lat_cell", "lon_cell"]).size().reset_index(name="weight")

    folder = _region_folder(region, weather_dir)
    weights.to_csv(folder / "weights.csv", index=False)
    return weights


def build_region_daily(
    region: str,
    cell_daily: pd.DataFrame,
    cell_size: float = DEFAULT_CELL_SIZE,
    *,
    weather_dir: Path = WEATHER_DIR,
) -> pd.DataFrame:
    """Aggregate cell-level daily weather to one region.

    The aggregation is weighted by how many of the region's 1 000 sample
    points fell into each cell.

    Parameters
    ----------
    region : str
        Normalised region id, e.g. ``NO3`` or ``VASS1``.
    cell_daily : pandas.DataFrame
        Output of :func:`fetch_cell_weather`.
    cell_size : float, optional
        Grid size. Default is 0.5.
    weather_dir : pathlib.Path, optional
        Output directory.

    Returns
    -------
    pandas.DataFrame
        Daily region averages with columns ``time``,
        ``temperature_2m``, ``precipitation`` and ``wind_speed_10m``.
    """
    weights = _region_weights(region, cell_size, weather_dir)
    merged = cell_daily.merge(weights, on=["lat_cell", "lon_cell"], how="inner")

    if merged.empty:
        raise ValueError(f"No grid cells matched the sample points for {region}")

    value_cols = list(DAILY_VARIABLES)
    weighted = merged[value_cols].mul(merged["weight"], axis=0)
    weighted["time"] = merged["time"].to_numpy()
    weighted["weight"] = merged["weight"].to_numpy()

    sums = weighted.groupby("time").sum()
    result = sums[value_cols].div(sums["weight"], axis=0).reset_index()
    result = result.sort_values("time").reset_index(drop=True)
    result = result.rename(columns=APP_COLUMNS)

    folder = _region_folder(region, weather_dir)
    result.to_parquet(folder / "daily.parquet", index=False)
    print(f"{region}: {len(result)} daily rows -> {folder / 'daily.parquet'}")

    return result


def build_norway_daily(
    *,
    weather_dir: Path = WEATHER_DIR,
) -> pd.DataFrame:
    """Build the area-weighted Norway average from NO1-NO5.

    The weights are the polygon areas of the five electricity areas in
    EPSG:3035.

    Parameters
    ----------
    weather_dir : pathlib.Path, optional
        Directory containing the per-region folders.

    Returns
    -------
    pandas.DataFrame
        Daily Norway averages with the same columns as the region files.
    """
    import geopandas as gpd

    shapefile = REGIONS_DIR / "electricity_areas.shp"
    areas = gpd.read_file(shapefile).to_crs(3035)
    areas["area_id"] = areas["budomr"].str.replace(" ", "", regex=False)
    weights = areas.set_index("area_id").geometry.area

    value_cols = ["temperature_2m", "precipitation", "wind_speed_10m"]
    frames = []

    for region in NORWAY_REGIONS:
        path = weather_dir / region / "daily.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Build {region} before the Norway average: {path}")
        frame = pd.read_parquet(path)
        frame["weight"] = float(weights.loc[region])
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    weighted = combined[value_cols].mul(combined["weight"], axis=0)
    weighted["time"] = combined["time"].to_numpy()
    weighted["weight"] = combined["weight"].to_numpy()

    sums = weighted.groupby("time").sum()
    result = sums[value_cols].div(sums["weight"], axis=0).reset_index()
    result = result.sort_values("time").reset_index(drop=True)

    folder = _region_folder("NO", weather_dir)
    result.to_parquet(folder / "daily.parquet", index=False)
    print(f"NO: {len(result)} daily rows -> {folder / 'daily.parquet'}")

    return result


def download_all_regions(
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    *,
    cell_size: float = DEFAULT_CELL_SIZE,
    batch_size: int = 50,
    weather_dir: Path = WEATHER_DIR,
    force: bool = False,
) -> dict[str, pd.DataFrame]:
    """Download and aggregate weather for every region.

    This is the one-call entry point::

        download_all_regions()

    It builds the shared 0.5 degree cells, downloads their daily weather,
    writes one folder per region, and builds the Norway average.

    Returns
    -------
    dict of str to pandas.DataFrame
        Daily data for ``NO1``-``NO5``, ``VASS1``-``VASS3`` and ``NO``.
    """
    cells = build_cells(cell_size, weather_dir=weather_dir, force=force)
    cell_daily = fetch_cell_weather(
        cells,
        start,
        end,
        cell_size=cell_size,
        batch_size=batch_size,
        weather_dir=weather_dir,
        force=force,
    )

    result = {}
    for region in REGIONS:
        result[region] = build_region_daily(
            region,
            cell_daily,
            cell_size,
            weather_dir=weather_dir,
        )

    result["NO"] = build_norway_daily(
        weather_dir=weather_dir,
    )
    return result


# ---------------------------------------------------------------------------
# 4. MongoDB
# ---------------------------------------------------------------------------


def upload_weather_to_mongo(
    regions: list[str] | None = None,
    *,
    collection_name: str = DEFAULT_COLLECTION,
    weather_dir: Path = WEATHER_DIR,
    client: MongoClient | None = None,
) -> dict[str, int]:
    """Upload the per-region daily weather to MongoDB.

    One collection is used for all regions: ``entsoE.weather``. Each
    document has ``region_id``, ``year``, ``time``, ``temperature_2m``,
    ``precipitation`` and ``wind_speed_10m``. Existing documents for a
    region are replaced, so the function is safe to re-run.

    Parameters
    ----------
    regions : list of str, optional
        Regions to upload. Default is all regions plus ``NO``.
    collection_name : str, optional
        Collection name. Default is ``weather``.
    weather_dir : pathlib.Path, optional
        Directory containing the per-region folders.
    client : pymongo.MongoClient, optional
        Existing client. If omitted, one is created and closed.

    Returns
    -------
    dict of str to int
        Number of documents inserted per region.
    """
    regions = regions or ALL_REGIONS
    owns_client = client is None

    if client is None:
        client = MongoClient(_mongo_uri(), serverSelectionTimeoutMS=20_000)

    client.admin.command("ping")
    collection = client["entsoE"][collection_name]

    inserted = {}

    for region in regions:
        path = weather_dir / region / "daily.parquet"
        if not path.exists():
            print(f"Skipping {region}: {path} does not exist")
            continue

        frame = pd.read_parquet(path)
        frame["time"] = pd.to_datetime(frame["time"]).dt.to_pydatetime()
        frame["region_id"] = region
        frame["year"] = pd.to_datetime(frame["time"]).dt.year

        records = frame[
            [
                "region_id",
                "year",
                "time",
                "temperature_2m",
                "precipitation",
                "wind_speed_10m",
            ]
        ].to_dict("records")

        years = sorted(int(y) for y in frame["year"].unique())
        collection.delete_many({"region_id": region, "year": {"$in": years}})
        collection.insert_many(records)
        inserted[region] = len(records)
        print(f"Uploaded {len(records)} documents for {region}")

    collection.create_index([("region_id", 1), ("year", 1), ("time", 1)])

    if owns_client:
        client.close()

    return inserted


def load_weather(
    region_id: str,
    start: str | None = None,
    end: str | None = None,
    *,
    collection_name: str = DEFAULT_COLLECTION,
    client: MongoClient | None = None,
) -> pd.DataFrame:
    """Load daily weather for one region from MongoDB.

    Parameters
    ----------
    region_id : str
        Normalised region id, e.g. ``NO3`` or ``VASS1``.
    start, end : str, optional
        Inclusive date range.
    collection_name : str, optional
        Collection name. Default is ``weather``.
    client : pymongo.MongoClient, optional
        Existing client. If omitted, one is created and closed.

    Returns
    -------
    pandas.DataFrame
        Columns ``time``, ``temperature_2m``, ``precipitation`` and
        ``wind_speed_10m``.
    """
    owns_client = client is None

    if client is None:
        client = MongoClient(_mongo_uri(), serverSelectionTimeoutMS=20_000)

    query: dict = {"region_id": region_id}
    if start is not None or end is not None:
        query["time"] = {}
        if start is not None:
            query["time"]["$gte"] = pd.Timestamp(start).to_pydatetime()
        if end is not None:
            query["time"]["$lt"] = (
                pd.Timestamp(end) + pd.Timedelta(days=1)
            ).to_pydatetime()

    collection = client["entsoE"][collection_name]
    records = list(collection.find(query, {"_id": 0}))

    if owns_client:
        client.close()

    if not records:
        return pd.DataFrame(
            columns=[
                "time",
                "temperature_2m",
                "precipitation",
                "wind_speed_10m",
            ]
        )

    frame = pd.DataFrame(records).sort_values("time")
    frame["time"] = pd.to_datetime(frame["time"])
    return frame.reset_index(drop=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    download = subparsers.add_parser("download", help="Download and aggregate")
    download.add_argument("--start", default=DEFAULT_START)
    download.add_argument("--end", default=DEFAULT_END)
    download.add_argument("--cell-size", type=float, default=DEFAULT_CELL_SIZE)
    download.add_argument("--batch-size", type=int, default=50)
    download.add_argument("--force", action="store_true")

    upload = subparsers.add_parser("upload", help="Upload daily data to MongoDB")
    upload.add_argument("--collection", default=DEFAULT_COLLECTION)

    all_parser = subparsers.add_parser("all", help="Download, aggregate, and upload")
    all_parser.add_argument("--start", default=DEFAULT_START)
    all_parser.add_argument("--end", default=DEFAULT_END)
    all_parser.add_argument("--cell-size", type=float, default=DEFAULT_CELL_SIZE)
    all_parser.add_argument("--batch-size", type=int, default=50)
    all_parser.add_argument("--force", action="store_true")
    all_parser.add_argument("--collection", default=DEFAULT_COLLECTION)

    args = parser.parse_args()

    if args.command == "download":
        download_all_regions(
            args.start,
            args.end,
            cell_size=args.cell_size,
            batch_size=args.batch_size,
            force=args.force,
        )
    elif args.command == "upload":
        upload_weather_to_mongo(collection_name=args.collection)
    elif args.command == "all":
        download_all_regions(
            args.start,
            args.end,
            cell_size=args.cell_size,
            batch_size=args.batch_size,
            force=args.force,
        )
        upload_weather_to_mongo(collection_name=args.collection)


if __name__ == "__main__":
    main()
