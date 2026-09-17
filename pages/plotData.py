import streamlit as st
from utils.reservoirsSelect import reservoirsSelect
from utils.dataLoaders import load_Reservoirs

st.title("Nullam ac ornare tellus.")
st.write("Duis eget sollicitudin justo. Pellentesque aliquam congue turpis sed aliquet. Etiam vitae nulla non sem elementum vulputate. ")

fullReservoirs = load_Reservoirs()
fullColumns = fullReservoirs.columns

optionsColumns = st.selectbox("Select what columns to display", fullColumns)
st.write(optionsColumns)