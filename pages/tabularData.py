import streamlit as st
import pandas as pd

reservoirs = pd.read_csv("/data/reservoirs.csv")
reservoirsDF = pd.DataFrame(reservoirs)

st.title("Mauris lorem")
st.write("elis, consectetur id mollis sit amet, vulputate non libero. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris eros purus, sagittis in finibus eu, ultricies sit amet nisi. Cras at sagittis eros.")

st.data_editor(
    reservoirsDF,
    column_config={
        "somm": st.column_config.LineChartColumn(
            "filler text",
            width="medium",
            help="wtf is this my man",
            y_min=100,
            y_max=100
    )},
)
