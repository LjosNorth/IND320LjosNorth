import pandas as pd
import streamlit as st
import plotly
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

# settings
pd.options.plotting.backend = "plotly"

st.title("Nullam ac ornare tellus.")
st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

fullReservoirs = load_Reservoirs()

# Select Box for Columns
fullColumns = fullReservoirs.columns.to_list()
fullColumns.append("All columns")
# optionColumns = ""
optionsColumns = st.selectbox("Select what columns to display", fullColumns)

#slider
fullReservoirs["dato_Id"] = pd.to_datetime(fullReservoirs["dato_Id"]).sort_values()
minMonth = fullReservoirs["dato_Id"].min().month
maxMonth = (fullReservoirs["dato_Id"].max().year-fullReservoirs["dato_Id"].min().year)*12+fullReservoirs["dato_Id"].max().month
months = st.slider("Choose nr. of months to look at", minMonth, maxMonth)

#get & plotting data
if optionsColumns == "":
    pass
elif optionsColumns == "All columns":
    reservoirs = reservoirsSelect(fullReservoirs, [], months)
else:
    reservoirs = reservoirsSelect(fullReservoirs, [optionsColumns], months)
    reservoirs.plot(kind="scatter", x="dato_Id", y="valor")
