import streamlit as st
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

st.title("Nullam ac ornare tellus.")
st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

fullReservoirs = load_Reservoirs()
fullColumns = fullReservoirs.columns
fullColumns.append("All columns")

# Select Box for Columns
optionsColumns = st.selectbox("Select what columns to display", fullColumns)
st.write(optionsColumns)

#slider
fullReservoirs["date_Id"] = fullReservoirs["date_Id"].to_timestamp().sort_values(by="date_Id")
minMonth = fullReservoirs["date_Id"].min().month
maxMonth = fullReservoirs["date_Id"].max().year*12+fullReservoirs["date_Id"].max().month
months = st.slider("Choose timelength to look at", minMonth, maxMonth)
st.write(months)