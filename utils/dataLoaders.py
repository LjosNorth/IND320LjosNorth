"""
Loads various data, is called elsewhere to be made use of
"""

from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from pymongo import MongoClient

# API column names -> names used by the rest of the app
MAGASIN_RENAME = {
    "dato_Id": "date (y-m-d)",
    "iso_aar": "year",
    "iso_uke": "week",
    "fyllingsgrad": "filled degree",
    "kapasitet_TWh": "capacity_Twh",
    "fylling_TWh": "fill_Twh",
    "neste_Publiseringsdato": "next_PublicizingDate",
    "fyllingsgrad_forrige_uke": "filled degree last week",
    "endring_fyllingsgrad": "change in filled degree",
}


# loading the reservoirs data
@st.cache_data
def load_Reservoirs_cvs():
    """WARN: legacy, use no longer"""
    ROOT = Path(__file__).resolve().parent.parent
    RESERVOIRS_FILE = ROOT / "data" / "reservoirs.csv"
    return pd.read_csv(RESERVOIRS_FILE)


@st.cache_data
def _fetch_magazine_data():
    """Download the full Magasinstatistikk dataset once and cache it.

    The NVE endpoint has no date parameters (they are ignored), so the
    download interval is applied in load_magazine_data_api() below.
    """
    API = (
        "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"
    )
    data = requests.get(API, timeout=120).json()
    magasinDF = pd.DataFrame(data).rename(columns=MAGASIN_RENAME)
    magasinDF["date (y-m-d)"] = pd.to_datetime(magasinDF["date (y-m-d)"])
    return magasinDF


def load_magazine_data_api(start=None, end=None):
    """Return Magasinstatistikk data, optionally trimmed to [start, end].

    Parameters:
        start: first date to keep (inclusive), e.g. "2020-01-01"
        end:   last date to keep (inclusive), e.g. "2020-12-31"
    """
    magasinDF = _fetch_magazine_data().copy()

    if start is not None:
        magasinDF = magasinDF[magasinDF["date (y-m-d)"] >= pd.Timestamp(start)]
    if end is not None:
        magasinDF = magasinDF[magasinDF["date (y-m-d)"] <= pd.Timestamp(end)]

    return magasinDF.sort_values("date (y-m-d)").reset_index(drop=True)


@st.cache_data
def load_mongoDB_transmission_data():
    """loads ENTSO_E data from MongoDB"""
    USR = st.secrets["usernameMongoDB"]
    PWD = st.secrets["passwordMongoDB"]
    uri = f"mongodb+srv://{USR}:{PWD}@ind320db.peyqaxm.mongodb.net/?appName=IND320DB"
    client = MongoClient(uri)

    database = client["entsoE"]
    collection = database["tranmissionData"]

    data = pd.DataFrame(list(collection.find()))
    client.close()

    # Mongo adds an ObjectId column that pandas/plotly cannot use
    data = data.drop(columns=["_id"], errors="ignore")
    if "time" in data.columns:
        data["time"] = pd.to_datetime(data["time"])
        data = data.sort_values("time").reset_index(drop=True)

    return data


@st.cache_data
def load_mongoDB_weather_data(
    region: str | None, startDate: str = "2024-01-01", endDate: str = "2024-12-31"
) -> pd.DataFrame:
    """loads Open-Meteo weather data for specified region"""

    if region is None:
        return pd.DataFrame()

    USR = st.secrets["usernameMongoDB"]
    PWD = st.secrets["passwordMongoDB"]
    uri = f"mongodb+srv://{USR}:{PWD}@ind320db.peyqaxm.mongodb.net/?appName=IND320DB"
    client = MongoClient(uri)

    database = client["entsoE"]
    collection = database["weather"]

    query = {
        "region_id": region,
        "time": {
            "$gte": pd.Timestamp(startDate).to_pydatetime(),
            "$lt": (pd.Timestamp(endDate) + pd.Timedelta(days=1)).to_pydatetime(),
        },
    }

    try:
        data = pd.DataFrame(list(collection.find(query, {"_id": 0})))
    finally:  # new toy hype
        client.close()

    if data.empty:
        return data

    if "time" in data.columns:
        data["time"] = pd.to_datetime(data["time"])
        data = data.sort_values("time").reset_index(drop=True)

    return data
