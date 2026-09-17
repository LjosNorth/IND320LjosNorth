import streamlit as st
import pandas as pd

reservoirs = pd.read_csv("data/reservoirs.csv")
reservoirsDF = pd.DataFrame(reservoirs)

st.title("Mauris lorem")
st.write("elis, consectetur id mollis sit amet, vulputate non libero. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris eros purus, sagittis in finibus eu, ultricies sit amet nisi. Cras at sagittis eros.")

st.write("with column config")
st.data_editor(
    reservoirsDF,
    column_config={
        "omrnr": st.column_config.LineChartColumn(
            "filler text",
            width="medium",
            help="wtf is this my man",
            y_min=1,
            y_max=100
    )},
    disabled=True
)

st.write("with column config")
st.data_editor(
    reservoirsDF,
    disabled=True
)