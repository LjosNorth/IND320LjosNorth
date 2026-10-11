'''
Loads various data, is called elsewhere to be made use of
'''
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import requests

# loading the reservoirs data
@st.cache_data
def load_Reservoirs_cvs():
    '''WARN: legacy, use no longer'''
    ROOT = Path(__file__).resolve().parent.parent
    RESERVOIRS_FILE = ROOT / "data" / "reservoirs.csv"
    return pd.read_csv(RESERVOIRS_FILE)

@st.cache_data
def load_magazine_data_api():
    '''loads from magasinstatistikk'''
    API = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"
    data = requests.get(API).json()
    magasinDF = pd.DataFrame(data)
    magasinDF = magasinDF.rename(columns={
        "dato_Id": "date (y-m-d)",
        "iso_aar": "year",
        "iso_uke": "week",
        "fyllingsgrad": "filled degree",
        "kapasitet_TWh": "capacity_Twh",
        "fylling_TWh": "fill_Twh",
        "neste_Publiseringsdato": "next_PublicizingDate",
        "fyllingsgrad_forrige_uke": "filled degree last week",
        "endring_fyllingsgrad": "change in filled degree"
    })
    return magasinDF