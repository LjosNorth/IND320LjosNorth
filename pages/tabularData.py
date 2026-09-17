import streamlit as st
import pandas as pd
from utils.reservoirsSelect import reservoirsSelect

@st.cache_data
def load_Reservoirs():
    return pd.read_csv("data/reservoirs.csv")

st.title("Mauris lorem")
st.write("elis, consectetur id mollis sit amet, vulputate non libero. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris eros purus, sagittis in finibus eu, ultricies sit amet nisi. Cras at sagittis eros.")

reservoirsDF = reservoirsSelect(load_Reservoirs(),columns=["fyllingsgrad", "kapasitet_TWh", "fylling_TWh"], months=1)
columns = reservoirsDF.columns
table_data = pd.DataFrame({
    "column": columns,
    "first month": [reservoirsDF[columns].tolist for columns in reservoirsDF.columns],
})

st.data_editor(
    table_data,
    column_config={
        "name": st.column_config.TextColumn("Reservoirs"),
        "first month": st.column_config.LineChartColumn(
            "first month",
            width="medium",
            y_min=0,
            y_max=100,
            help="this better work"
        )
    },
    disabled=True
)