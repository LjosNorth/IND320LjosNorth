from pathlib import Path
import pandas as pd
import streamlit as st

# loading the reservoirs data
@st.cache_data
def load_Reservoirs():
    ROOT = Path(__file__).resolve().parent.parent
    RESERVOIRS_FILE = ROOT / "data" / "reservoirs.csv"
    return pd.read_csv(RESERVOIRS_FILE)
