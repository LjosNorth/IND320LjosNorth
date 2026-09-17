from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
RESERVOIRS_FILE = ROOT / "data" / "reservoirs.csv"
@st.cache_data
def load_Reservoirs():
    return pd.read_csv(RESERVOIRS_FILE)
