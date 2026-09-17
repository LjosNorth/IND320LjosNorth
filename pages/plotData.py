import pandas as pd
import streamlit as st
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

st.title("Nullam ac ornare tellus.")
st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

fullReservoirs = load_Reservoirs()
fullColumns = fullReservoirs.columns.to_list()
fullColumns.append("All columns")

# Select Box for Columns
optionsColumns = st.selectbox("Select what columns to display", fullColumns)
st.write(optionsColumns)

#slider
fullReservoirs["dato_Id"] = pd.to_datetime(fullReservoirs["dato_Id"]).sort_values()
minMonth = fullReservoirs["dato_Id"].min().month
maxMonth = fullReservoirs["dato_Id"].max().year*12+fullReservoirs["dato_Id"].max().month
months = st.slider("Choose timelength to look at", minMonth, maxMonth)
st.write(months)